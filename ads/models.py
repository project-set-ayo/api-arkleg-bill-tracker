"""Models for Ads."""

from django.db import models
from model_utils.models import TimeStampedModel

ads = [
    {
        "title": "Amazon Tech Deals",
        "image": "https://m.media-amazon.com/images/I/61w69RXYcNL._AC_UL320_.jpg",
        "link": "https://www.amazon.com/deals?tag=your-affiliate-tag",
        "weight": 5,
    },
    {
        "title": "Expedia Travel Deals",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Expedia_Logo.svg/2560px-Expedia_Logo.svg.png",
        "link": "https://www.expedia.com/",
        "weight": 3,
    },
    {
        "title": "Udemy Programming Courses",
        "image": "https://www.udemy.com/staticx/udemy/images/v7/logo-udemy.svg",
        "link": "https://www.udemy.com/courses/development/?couponCode=YOURCOUPON",
        "weight": 8,
    },
    {
        "title": "Nike Fitness Gear",
        "image": "https://www.nike.com/etc.clientlibs/settings/wcm/designs/nike/clientlibs/global/resources/img/nike-logo.png",
        "link": "https://www.nike.com/w/training-gear-8n2l6",
        "weight": 2,
    },
    {
        "title": "Coursera Online Courses",
        "image": "https://d3njjcbhbojbot.cloudfront.net/web/images/favicons/android-chrome-192x192.png",
        "link": "https://www.coursera.org/",
        "weight": 4,
    },
]


class Ad(TimeStampedModel):
    title = models.CharField(max_length=255)
    image = models.URLField()  # Using URLField for external images
    link = models.URLField()
    weight = models.PositiveIntegerField(
        default=1
    )  # Higher weight = more frequent display
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Ad: {self.title} (Weight: {self.weight})"
