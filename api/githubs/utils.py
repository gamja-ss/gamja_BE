import requests
from coins.models import Coin
from django.db import transaction
from django.utils import timezone

from .models import Github


def get_github_commits(github_username, github_token):
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          totalCommitContributions
        }
      }
    }
    """

    variables = {"username": github_username}
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        response.raise_for_status()
        data = response.json()
        return data["data"]["user"]["contributionsCollection"][
            "totalCommitContributions"
        ]
    except requests.RequestException as e:
        print(f"GitHub API 요청 실패: 사용자 {github_username}, 에러: {str(e)}")
    except KeyError as e:
        print(f"GitHub API 응답 파싱 실패: 사용자 {github_username}, 에러: {str(e)}")
    except Exception as e:
        print(f"예상치 못한 에러 발생: 사용자 {github_username}, 에러: {str(e)}")

    return None


def set_initial_github_commits(user):
    total_commits = get_github_commits(user.username, user.github_access_token)
    if total_commits is not None:
        user.github_initial_commits = total_commits
        user.github_initial_date = timezone.now().date()
        user.save()

        Github.objects.create(
            user=user, date=user.github_initial_date, commit_num=total_commits
        )
        print(
            f"초기 GitHub 커밋 정보 설정 완료: 사용자 {user.id}, 커밋 수 {total_commits}"
        )
        return True
    return False


@transaction.atomic
def update_user_github_commits(user):
    if not user.github_access_token or not user.username:
        print(f"GitHub 정보 없음: 사용자 {user.id}")
        return None

    total_commits = get_github_commits(user.username, user.github_access_token)
    if total_commits is None:
        return None

    now = timezone.now()

    previous_github = Github.objects.filter(user=user).order_by("-date", "-id").first()

    if previous_github:
        commit_difference = total_commits - previous_github.commit_num

    if commit_difference > 0:
        coins_earned = commit_difference
        exp_earned = commit_difference

        Coin.objects.create(
            user=user,
            verb="github",
            coins=coins_earned,
            timestamp=now,
        )

        user.increase_exp(exp_earned)

        print(
            f"코인 및 경험치 증가: 사용자 {user.username}, 획득 코인: {coins_earned}, 경험치: {exp_earned}, 새 티어: {user.user_tier}"
        )
    github_record, created = Github.objects.update_or_create(
        user=user, date=now.date(), defaults={"commit_num": total_commits}
    )

    print(
        f"GitHub 커밋 수 업데이트 성공: 사용자 {user.username}, 커밋 수 {total_commits}"
    )
    return github_record
