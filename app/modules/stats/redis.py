import redis
import envkey
import arrow
# from cacheops import cached
from consoler import console
from collections import defaultdict


class RedisViewCounts():

    def __init__(self, *args, **kwargs):
        self.conn = redis.StrictRedis(
            host=envkey.get("REDIS_HOST"),
            port=envkey.get("REDIS_PORT", 6379),
            password=envkey.get("REDIS_PASSWORD"),
            db=10,
            decode_responses=True
        )
        self._set = "_stats_set"
        self._hash = "_stats_hash"
        super().__init__(*args, **kwargs)

    def hit(self, page_id: int) -> int:
        """Record a hit against a page.

        Args:
            page_id (int): The int ID of the page that's received a hit

        Returns:
            int: The view count for that page for today
        """
        key = self._key(page_id)
        result = self.conn.hincrby(name=self._hash, key=key)
        self.conn.zadd(self._set, {key: result})
        return result

    def popular_with_counts(self, limit: int = 100):
        """Return the `limit` most popular pages with their view counts.

        Args:
            limit (int, optional): How many results to return

        Returns:
            list: List of page IDs
        """
        ranked = self._ranked()
        return ranked[:limit]

    def popular(self, limit: int = 100):
        """Return the `limit` most popular pages.

        Args:
            limit (int, optional): How many results to return

        Returns:
            list: List of page IDs
        """
        ranked = self._ranked()
        return [item[0] for item in ranked[:limit]]

    def _ranked(self):
        """Get a ranked list of page_ids and their view counts as tuples: (page_id, count)

        [
         (9, 108.0),
         (8, 96.0),
         (7, 84.0),
         (6, 72.0),
         (5, 60.0),
         (4, 48.0),
         (3, 36.0),
         (2, 24.0),
         (1, 12.0),
        ]

        Returns:
            list: The list of ranked page ids
        """
        self._expire()
        totals = defaultdict(int)
        dailies = self.conn.zrange(self._set, 0, -1, desc=True, withscores=True)
        for tup in dailies:
            key = tup[0]
            page_id = key.split('_')[1]
            score = tup[1]
            totals[int(page_id)] += score

        ranked = sorted(totals.items(), key=lambda x: x[1], reverse=True)
        return ranked

    def _expire(self):
        """Gets all the results from self._set and self._hash and deletes the keys
        older than one week.
        conn.zrange on the _set returns a list of keys...
        [
            '2022-06-20_9',
            '2022-06-19_9',
            '2022-06-18_9',
            '2022-06-20_8',
        ]
        """
        try:
            oldest = arrow.now().shift(days=-7)
            # To delete a bunch of keys from a hash, we do it in one command, so we create
            # a list to store the keys in until we're ready.
            hash_keys: list = []
            # Expire the set
            set_list = self.conn.zrange(self._set, 0, -1)
            for item in set_list:
                date = arrow.get(item.split('_')[0])
                if date < oldest:
                    self.conn.zrem(self._set, item)
                    hash_keys.append(item)

            # Finally clear the hash keys
            if len(hash_keys):
                self.conn.hdel(self._hash, *hash_keys)
        except Exception as error:
            console.warn(error)
            return False
        return True

    def _key(self, page_id):
        """Get the key we want to use in both the set and the hash.

        Args:
            page_id (int): A page ID

        Returns:
            str: The key to use
        """
        date = arrow.now().format("YYYY-MM-DD")
        return f"{date}_{page_id}"

    def _purge(self):
        self.conn.delete(self._set)
        self.conn.delete(self._hash)
