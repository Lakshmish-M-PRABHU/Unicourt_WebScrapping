import json
import requests


def fetch_full_user_profile(username):
  url = "https://leetcode.com/graphql/"

  combined_query = """
    query combinedUserProfile($username: String!, $userSlug: String!) {
      allQuestionsCount {
        difficulty
        count
      }
      matchedUser(username: $username) {
        submitStats {
          acSubmissionNum {
            difficulty
            count
            submissions
          }
        }
      }
      userContestBaseRating(username: $userSlug) {
        rating
        attendedContestsCount
      }
    }
    """

  payload = {
      "operationName": "combinedUserProfile",
      "query": combined_query,
      "variables": {"username": username, "userSlug": username},
  }

  headers = {
      "Content-Type": "application/json",
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/120.0.0.0 Safari/537.36"
      ),
      "Referer": f"https://leetcode.com/{username}/",
  }

  response = requests.post(url, json=payload, headers=headers)
  if response.status_code == 200:
    return response.json()
  return None


if __name__ == "__main__":
  # Take dynamic user input from the terminal
  target_username = input("Enter LeetCode username: ").strip()

  if not target_username:
    print("Username cannot be empty!")
  else:
    print(f"Fetching data for {target_username}...")
    result = fetch_full_user_profile(target_username)

    if result and result.get("data") and result["data"].get("matchedUser"):
      data = result["data"]

      # Extract Solved Problems by Difficulty
      solved_data = data.get("matchedUser", {}).get("submitStats", {}).get("acSubmissionNum", [])
      solved_counts = {item["difficulty"]: item["count"] for item in solved_data}

      easy_solved = solved_counts.get("Easy", 0)
      medium_solved = solved_counts.get("Medium", 0)
      hard_solved = solved_counts.get("Hard", 0)
      total_solved = solved_counts.get("All", 0)

      # Extract Contest Data
      contest_data = data.get("userContestBaseRating") or {}
      rating = round(contest_data.get("rating", 0))
      attended = contest_data.get("attendedContestsCount", 0)

      # Format into a natural sentence
      summary_sentence = (
          f"LeetCode Profile for {target_username}: "
          f"They have solved a total of {total_solved} problems "
          f"({easy_solved} Easy, {medium_solved} Medium, and {hard_solved} Hard). "
          f"In contests, they have attended {attended} events "
          f"and earned a rating of {rating}."
      )

      print("\n" + summary_sentence)
    else:
      print(f"Could not retrieve profile data. Please check if the username '{target_username}' exists.")
