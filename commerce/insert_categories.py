from shop.models import Category

categories = [
    ('Electronics', 'Devices and gadgets including phones, laptops, tablets, etc.'),
    ('Fashion', 'Clothing, accessories, and footwear for men, women, and children.'),
    ('Home & Kitchen', 'Furniture, appliances, cookware, and home decor.'),
    ('Books', 'Printed and digital books, magazines, and educational materials.'),
    ('Health & Beauty', 'Personal care, skincare, wellness, and beauty products.'),
    ('Sports & Outdoors', 'Sporting goods, camping gear, fitness equipment, and outdoor apparel.'),
    ('Toys & Games', 'Toys, board games, puzzles, and activities for children and adults.'),
    ('Groceries', 'Food, beverages, and other essential household supplies.'),
    ('Jewelry & Watches', 'Rings, necklaces, bracelets, watches, and other luxury items.'),
    ('Automotive', 'Car parts, accessories, tools, and automotive care products.'),
    ('Music & Instruments', 'Musical instruments, gear, and accessories.'),
    ('Baby & Kids', 'Baby clothes, toys, strollers, and essentials for children.'),
    ('Office Supplies', 'Stationery, furniture, and supplies for home and office work.'),
    ('Art & Crafts', 'Supplies for painting, drawing, knitting, and DIY projects.'),
    ('Furniture', 'Bedroom, living room, office, and outdoor furniture.'),
    ('Gardening & Outdoors', 'Plants, seeds, tools, and accessories for gardening and outdoor spaces.'),
    ('Pet Supplies', 'Pet food, toys, grooming, and care products for pets.'),
    ('DIY & Tools', 'Tools, hardware, and materials for home improvement and repairs.'),
    ('Software & Technology', 'Software applications, operating systems, and tech services.'),
    ('Cameras & Photography', 'Cameras, lenses, tripods, and photography accessories.'),
    ('Video Games', 'Console and PC games, accessories, and gaming hardware.'),
    ('Watches & Accessories', 'Watches, handbags, sunglasses, and fashion accessories.'),
    ('Health & Wellness', 'Supplements, fitness equipment, and products for healthy living.'),
    ('Gifts & Special Occasion', 'Gifts for birthdays, weddings, anniversaries, and other celebrations.'),
    ('Musical Instruments', 'Instruments, accessories, and music equipment for musicians.'),
    ('Food & Beverage', 'Gourmet food, snacks, and specialty drinks.'),
    ('Smart Home', 'Smart devices and home automation products.'),
    ('Photography & Imaging', 'Photography gear, printers, and imaging technology.'),
    ('Luxury Goods', 'High-end fashion, jewelry, and luxury lifestyle items.'),
    ('Luggage & Bags', 'Travel bags, suitcases, backpacks, and luggage accessories.'),
    ('Shoes', 'Footwear for men, women, and children.'),
    ('Party & Celebration', 'Decorations, costumes, and party supplies.'),
    ('Cleaning Supplies', 'Household and industrial cleaning products and tools.'),
    ('Wine & Spirits', 'Alcoholic beverages, wines, and spirits.'),
    ('Hardware', 'Fasteners, nails, screws, and other building hardware.'),
    ('Travel & Vacation', 'Travel services, vacation packages, and accessories.'),
    ('Appliances', 'Home and kitchen appliances, including refrigerators and microwaves.'),
    ('Mobile Phones & Accessories', 'Phones, chargers, cases, and accessories.'),
    ('Computers & Tablets', 'Laptops, desktops, tablets, and related accessories.'),
    ('Kitchenware', 'Cooking utensils, pots, pans, and kitchen tools.'),
    ('Home Improvement', 'Tools and products for renovation, construction, and home repairs.'),
    ('Stationery & Office', 'Office supplies such as paper, pens, and organizational tools.'),
    ('Virtual Products', 'Digital goods such as eBooks, software, and downloadable content.'),
    ('Subscription Services', 'Subscription boxes, membership services, and digital subscriptions.'),
    ('Collectibles', 'Rare items such as coins, stamps, figurines, and memorabilia.'),
    ('Religious & Spiritual', 'Items for religious practices, prayer, and meditation.'),
    ('Furniture & Lighting', 'Furniture, lighting fixtures, and decor for home and office spaces.'),
    ('Outdoor Adventure', 'Equipment and apparel for outdoor activities like hiking and trekking.'),
    ('Tools & Equipment', 'Hand tools, power tools, and construction equipment for professionals.'),
    ('Kitchen & Dining', 'Kitchen essentials like cutlery, tableware, and storage containers.'),
    ('Office Furniture', 'Desks, chairs, filing cabinets, and ergonomic furniture for offices.'),
    ('Gardening Tools', 'Tools and equipment for garden maintenance and landscaping.')
]

for name, description in categories:
    category, created = Category.objects.get_or_create(name=name, description=description)
    if created:
        print(f"Successfully inserted: {category.name}")
    else:
        print(f"Category already exists: {category.name}")
