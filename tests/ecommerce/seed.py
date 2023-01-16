
from ecommerce.models import *

def seed_database():
    seed_navigation_items()
    seed_products()


def seed_products():
    athletic_shoe = Product(name="Athletic Shoe", slug="athletic-shoe")
    athletic_shoe.save()

    athletic_shoe_color = VariantDimension(name="Color", slug="color", product=athletic_shoe)
    athletic_shoe_size = VariantDimension(name="Size", slug="size", product=athletic_shoe)

    athletic_shoe_color.save()
    athletic_shoe_size.save()

    for color in ["Red", "Blue", "Green"]:
        for size in ["10", "11", "12", "13"]:
            variant = Variant(name=f"{color} {size}", slug=f"color-{color}-size-{size}".lower(), product=athletic_shoe, price_in_cents_usd=50_000)
            variant.save()
            VariantDimensionValue(variant=variant, dimension=athletic_shoe_color, value=color).save()
            VariantDimensionValue(variant=variant, dimension=athletic_shoe_size, value=size).save()


def seed_navigation_items():
    men = NavigationItem(name="Men")
    men.save()

    women = NavigationItem(name="Women")
    women.save()

    mens_shoes = NavigationItem(name="Shoes", pathname="men/shoes", parent=men)
    mens_shoes.save()

    womens_shoes = NavigationItem(name="Shoes", pathname="women/shoes", parent=women)
    womens_shoes.save()

    mens_clothing = NavigationItem(name="Clothing", parent=men)
    mens_clothing.save()

    womens_clothing = NavigationItem(name="Clothing", parent=women)
    womens_clothing.save()

    mens_tees = NavigationItem(name="Tees", pathname="men/clothing/tees", parent=mens_clothing)
    mens_tees.save()
    
    womens_tees = NavigationItem(name="Tees", pathname="women/clothing/tees", parent=womens_clothing)
    womens_tees.save()
