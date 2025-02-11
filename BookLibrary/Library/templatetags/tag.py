from django import template
from django.utils.safestring import SafeText, mark_safe

from Library.models import UserRating


register = template.Library()

empty_star = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
                    <path 
                        d="m6.516 14.323-1.49 6.452a.998.998 0 0 0 1.529 1.057L12 18.202l5.445 3.63a1.001 1.001 0 0 0 1.517-1.106l-1.829-6.4 4.536-4.082a1 1 0 0 0-.59-1.74l-5.701-.454-2.467-5.461a.998.998 0 0 0-1.822 0L8.622 8.05l-5.701.453a1 1 0 0 0-.619 1.713l4.214 4.107zm2.853-4.326a.998.998 0 0 0 .832-.586L12 5.43l1.799 3.981a.998.998 0 0 0 .832.586l3.972.315-3.271 2.944c-.284.256-.397.65-.293 1.018l1.253 4.385-3.736-2.491a.995.995 0 0 0-1.109 0l-3.904 2.603 1.05-4.546a1 1 0 0 0-.276-.94l-3.038-2.962 4.09-.326z">
                    </path>
                </svg>"""

half_star = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"">
                <path 
                    d="M5.025 20.775A.998.998 0 0 0 6 22a1 1 0 0 0 .555-.168L12 18.202l5.445 3.63a1.001 1.001 0 0 0 1.517-1.106l-1.829-6.4 4.536-4.082a1 1 0 0 0-.59-1.74l-5.701-.454-2.467-5.461a.998.998 0 0 0-1.822-.001L8.622 8.05l-5.701.453a1 1 0 0 0-.619 1.713l4.214 4.107-1.491 6.452zM12 5.429l2.042 4.521.588.047h.001l3.972.315-3.271 2.944-.001.002-.463.416.171.597v.003l1.253 4.385L12 15.798V5.429z">
                </path>
            </svg>"""

star = """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24">
            <path 
                d="M21.947 9.179a1.001 1.001 0 0 0-.868-.676l-5.701-.453-2.467-5.461a.998.998 0 0 0-1.822-.001L8.622 8.05l-5.701.453a1 1 0 0 0-.619 1.713l4.213 4.107-1.49 6.452a1 1 0 0 0 1.53 1.057L12 18.202l5.445 3.63a1.001 1.001 0 0 0 1.517-1.106l-1.829-6.4 4.536-4.082c.297-.268.406-.686.278-1.065z">
            </path>
        </svg>"""


@register.simple_tag()
def book_rating(book_id: int, show_rating_amount: bool = False) -> SafeText:
    total_rating, total_review = UserRating.book_rating.select_related("user", "book").book_total(
        book_id=book_id
    ).values()

    review_num_string = f'<span class="dot">·</span><span>{total_review} Ratings</span>'

    if total_rating == None or total_review == None:
        return mark_safe("Not rated yet")

    mark = int(total_rating) / int(total_review)

    if mark >= 5:
        mark = 5

    average_mark_string = (
        f"<span>{ mark if mark.is_integer() else round(mark, 1)}/5</span>"
    )
    d = mark - int(mark)
    starts = star * int(mark)

    if d >= 0.5:
        empty_stars = empty_star * int(4 - int(mark))
        res = "".join(
            starts
            + half_star
            + empty_stars
            + average_mark_string
            + (review_num_string if show_rating_amount else "")
        )
    else:
        empty_stars = empty_star * int(5 - int(mark))
        res = "".join(
            starts
            + empty_stars
            + average_mark_string
            + (review_num_string if show_rating_amount else "")
        )

    return mark_safe(res)
