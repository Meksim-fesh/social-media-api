from post.models import Post

from celery import shared_task


@shared_task
def create_scheduled_post(post_id) -> None:
    try:
        post = Post.objects.get(id=post_id)
        post.publish()
    except Post.DoesNotExist:
        print(f"Scheduled post with id {post_id} does not exist")
