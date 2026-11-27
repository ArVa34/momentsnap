import io
import textwrap
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from catalog.models import Category, Item

E = Item.EventType
S = Item.Style

# Each product: (name, price, stock, event type, style, description)
CATALOG = [
    {
        "name": "Event Packages",
        "slug": "event-packages",
        "description": "Digital packages and bundles",
        "colours": ("#8a3b5c", "#ffffff"),
        "is_event_package": True,
        "children": [
            {
                "name": "Digital Packages",
                "slug": "digital-packages",
                "items": [
                    ("Essential Digital Package", "79.00", 999, E.ANY, "",
                     "A private QR gallery for one event, with timed photo challenges. Ideal for smaller celebrations."),
                    ("Premium Digital Package", "149.00", 999, E.ANY, "",
                     "Everything in Essential, with more challenges and a higher photo limit per guest. Our most popular choice."),
                    ("Unlimited Digital Package", "229.00", 999, E.ANY, "",
                     "No limits on challenges or photos for the whole night, for big celebrations with many guests."),
                ],
            },
            {
                "name": "Digital + Print Bundles",
                "slug": "digital-print-bundles",
                "items": [
                    ("Wedding Story Bundle", "299.00", 999, E.WEDDING, S.CLASSIC,
                     "The Premium package together with a hardcover album of your favourite guest photos."),
                    ("Christening Keepsake Bundle", "219.00", 999, E.CHRISTENING, S.FLORAL,
                     "A QR gallery for the christening and a soft floral album to keep the day's memories."),
                    ("Party Memories Bundle", "189.00", 999, E.BIRTHDAY, S.MINIMAL,
                     "A QR gallery for your party and a set of instant-style prints of the best shots."),
                ],
            },
        ],
    },
    {
        "name": "QR Table Cards",
        "slug": "qr-table-cards",
        "description": "Tent cards and flat cards",
        "colours": ("#f8f1f4", "#6f2f4a"),
        "is_event_package": False,
        "children": [
            {
                "name": "Tent Cards",
                "slug": "tent-cards",
                "items": [
                    ("Floral Tent Card (set of 10)", "24.00", 200, E.WEDDING, S.FLORAL,
                     "Folded table cards with a hand-drawn floral frame around your event's QR code."),
                    ("Rustic Kraft Tent Card (set of 10)", "22.00", 200, E.ANY, S.RUSTIC,
                     "Natural kraft paper cards with a simple twine-style border. Warm and relaxed."),
                    ("Minimal White Tent Card (set of 10)", "19.00", 200, E.ANY, S.MINIMAL,
                     "Clean white cards with your QR code and one line of text. Fits any decoration."),
                ],
            },
            {
                "name": "Flat Cards",
                "slug": "flat-cards",
                "items": [
                    ("Classic Gold Foil Flat Card (set of 10)", "29.00", 150, E.WEDDING, S.CLASSIC,
                     "Thick flat cards with gold foil lettering, made to stand in a table-number holder."),
                    ("Pastel Christening Flat Card (set of 10)", "21.00", 150, E.CHRISTENING, S.FLORAL,
                     "Soft pastel cards with small illustrations, designed for christenings."),
                    ("Corporate Flat Card (set of 10)", "18.00", 150, E.CORPORATE, S.MINIMAL,
                     "Simple cards with room for your company logo next to the QR code."),
                ],
            },
        ],
    },
    {
        "name": "Photo Albums",
        "slug": "photo-albums",
        "description": "Hardcover and layflat",
        "colours": ("#1f1a1d", "#f3c6d8"),
        "is_event_package": False,
        "children": [
            {
                "name": "Hardcover",
                "slug": "hardcover",
                "items": [
                    ("Linen Hardcover Album 30x30", "89.00", 40, E.WEDDING, S.CLASSIC,
                     "A linen-covered album with 30 pages for your favourite guest photos."),
                    ("Leather Hardcover Album 30x30", "139.00", 15, E.WEDDING, S.CLASSIC,
                     "A premium leather cover with debossed names and date. 40 pages."),
                    ("Kids Hardcover Album 20x20", "49.00", 30, E.CHRISTENING, S.FLORAL,
                     "A smaller album with a soft illustrated cover, perfect for christenings."),
                ],
            },
            {
                "name": "Layflat",
                "slug": "layflat",
                "items": [
                    ("Layflat Album 30x30, 40 pages", "169.00", 20, E.WEDDING, S.MINIMAL,
                     "Pages open completely flat, so photos can run across both sides without a gap."),
                    ("Layflat Album 25x25, 30 pages", "119.00", 25, E.ANY, S.MINIMAL,
                     "A slightly smaller layflat album for any celebration."),
                    ("Rustic Wood Cover Layflat Album", "199.00", 2, E.WEDDING, S.RUSTIC,
                     "A layflat album with a real wooden cover, engraved with your names. Limited stock."),
                ],
            },
        ],
    },
    {
        "name": "Prints & Canvas",
        "slug": "prints-canvas",
        "description": "Photo prints and canvas",
        "colours": ("#e9e2d8", "#3b3035"),
        "is_event_package": False,
        "children": [
            {
                "name": "Photo Prints",
                "slug": "photo-prints",
                "items": [
                    ("Matte Photo Prints 10x15 (set of 50)", "19.00", 300, E.ANY, "",
                     "Fifty matte prints of the photos you choose from your gallery."),
                    ("Glossy Photo Prints 13x18 (set of 30)", "17.00", 300, E.ANY, "",
                     "Thirty glossy prints in a slightly larger size."),
                    ("Instant-Style Prints (set of 40)", "22.00", 300, E.BIRTHDAY, S.MINIMAL,
                     "Square prints with a white border, great for a party wall."),
                ],
            },
            {
                "name": "Canvas",
                "slug": "canvas",
                "items": [
                    ("Canvas Print 40x60", "59.00", 30, E.ANY, S.CLASSIC,
                     "Your favourite photo on canvas, stretched over a wooden frame and ready to hang."),
                    ("Canvas Print 60x90", "89.00", 20, E.ANY, S.CLASSIC,
                     "A large canvas for the photo that deserves the main wall."),
                    ("Triptych Canvas Set", "129.00", 0, E.WEDDING, S.MINIMAL,
                     "Three matching canvases that tell your day in three moments. Currently out of stock."),
                ],
            },
        ],
    },
]


def make_placeholder(text, colours):
    """Draw a simple 1200x900 JPEG with the product name, in the category's colours."""
    background, foreground = colours
    image = Image.new("RGB", (1200, 900), background)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default(size=64)

    lines = textwrap.wrap(text, width=22)
    line_height = 80
    y = (900 - line_height * len(lines)) // 2
    for line in lines:
        width = draw.textlength(line, font=font)
        draw.text(((1200 - width) / 2, y), line, fill=foreground, font=font)
        y += line_height

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    return ContentFile(buffer.getvalue())


class Command(BaseCommand):
    help = "Create or update the demo catalogue: categories, products and placeholder images. Safe to run again."

    @transaction.atomic
    def handle(self, *args, **options):
        new_products = 0

        for top in CATALOG:
            parent, _created = Category.objects.update_or_create(
                slug=top["slug"],
                defaults={"name": top["name"], "description": top["description"], "parent": None},
            )
            for sub in top["children"]:
                category, _created = Category.objects.update_or_create(
                    slug=sub["slug"],
                    defaults={"name": sub["name"], "parent": parent},
                )
                for name, price, stock, event_type, style, description in sub["items"]:
                    item, created = Item.objects.update_or_create(
                        slug=slugify(name),
                        defaults={
                            "name": name,
                            "category": category,
                            "price": Decimal(price),
                            "stock": stock,
                            "event_type": event_type,
                            "style": style,
                            "description": description,
                            "is_event_package": top["is_event_package"],
                            "is_active": True,
                        },
                    )
                    new_products += created
                    if not item.image:
                        item.image.save(f"{item.slug}.jpg", make_placeholder(name, top["colours"]))

        total = Item.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Demo catalogue ready: {new_products} new products, {total} products in total."
        ))