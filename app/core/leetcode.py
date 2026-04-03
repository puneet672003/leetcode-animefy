from typing import Any

import httpx

from core.logger import Logger


class LeetCodeClientException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class LeetCodeClient:
    URL = "https://leetcode.com/graphql/"
    _client: httpx.AsyncClient | None = None

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._client is None or cls._client.is_closed:
            cls._client = httpx.AsyncClient()
        return cls._client

    @classmethod
    async def _make_request(
        cls, query: str, variables: dict, operation_name: str, username: str
    ) -> dict[str, Any]:
        payload = {
            "operationName": operation_name,
            "query": query,
            "variables": variables,
        }

        headers = {
            "Content-Type": "application/json",
            "Referer": f"https://leetcode.com/u/{username}/",
        }

        client = cls._get_client()
        try:
            response = await client.post(
                cls.URL, json=payload, headers=headers, timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            Logger.error(f"[LEETCODE] HTTP error for {username}: {e}")
            raise LeetCodeClientException(f"Request failed: {e}", status_code=502)

        try:
            data = response.json()
            if "errors" in data:
                Logger.warning(
                    f"[LEETCODE] GraphQL errors for {username}: {data['errors']}"
                )
                raise LeetCodeClientException("GraphQL error", status_code=400)
            return data["data"]
        except ValueError:
            Logger.error(f"[LEETCODE] Invalid JSON response for {username}")
            raise LeetCodeClientException("Invalid JSON response", status_code=502)

    @classmethod
    async def get_question_progress(cls, username: str) -> dict[str, Any]:
        query = """
        query userProfileUserQuestionProgressV2($userSlug: String!) {
          userProfileUserQuestionProgressV2(userSlug: $userSlug) {
            numAcceptedQuestions {
              count
              difficulty
            }
          }
        }
        """

        data = await cls._make_request(
            query=query,
            variables={"userSlug": username},
            operation_name="userProfileUserQuestionProgressV2",
            username=username,
        )

        try:
            return data["userProfileUserQuestionProgressV2"]["numAcceptedQuestions"]
        except (KeyError, TypeError):
            Logger.error(
                f"[LEETCODE] Unexpected response structure for {username}: {data}"
            )
            raise LeetCodeClientException("Unexpected response format", status_code=502)
