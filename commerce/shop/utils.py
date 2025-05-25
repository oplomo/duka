# utils.py
from .models import Order


def user_can_review(user, product):
    return Order.objects.filter(
        buyer=user, product=product, is_delivered=True, reviewed=False
    ).exists()

import hashlib
import json
from .models import Review

def generate_review_hash(review):
    review_data = {
        "rating": review.rating,
        "comment": review.comment,
        "reviewer_id": review.reviewer.id,
        "created_at": review.created_at.isoformat(),
    }
    review_json = json.dumps(review_data, sort_keys=True).encode()
    return hashlib.sha256(review_json).hexdigest()

def create_or_update_review(order, rating, comment, user):
    review, created = Review.objects.get_or_create(
        order=order, defaults={"reviewer": user}
    )

    # Update fields
    review.rating = rating
    review.comment = comment
    review.reviewer = user  # Safe to update

    review.save()  # Save first to populate created_at if it's new

    # Generate the new hash
    new_hash = generate_review_hash(review)

    # Now handle the update logic
    if created:
        # First time creation, just set the initial hash, no modification
        review.last_changed_hash = new_hash
        review.is_updated = False  # Not an update
        review.save()
        print("Review created.")
    else:
        # Already existed, check if hash changed
        if review.last_changed_hash != new_hash:
            review.last_changed_hash = new_hash
            review.is_updated = True  # Now it's an update
            review.save()
            print("Review was modified.")
        else:
            print("Review data is the same.")

    return review
