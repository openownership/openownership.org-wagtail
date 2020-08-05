# Stats Module

This page lets you collect page views per page per day, and then query against that, which enables blocks like Most Read, or Popular This Week.

## Install

Add `'modules.stats'` to your `INSTALLED_APPS`

Either add the `Countable` mixin to the pages that you want to record, or simply add an attribute `is_countable`. Then add the `ViewCountMiddleware` as the very first item in your middleware list. If you want this to work with wagtail-cache, then it definitely needs to come before `wagtailcache.cache.UpdateCacheMiddleware` - this doesn't affect wagtail-cache's ability to operate as the `ViewCountMiddleware` doesn't alter or affect the request or the response in any way.

```
MIDDLEWARE = [
    'modules.stats.middleware.ViewCountMiddleware',
    'wagtailcache.cache.UpdateCacheMiddleware',
    [...]
    'wagtailcache.cache.FetchFromCacheMiddleware',
]
```

## Usage

To get the most popular posts from the last 7 days..

```
Viewcount.objects.popular(7)

# As 7 is the default days count, you ccould also just call

ViewCount.objects.popular()
```

This will return a list of page IDs which you can then build a page query from. By default, we return the 100 most popular, but you can change the limit yourself too with a second parameter.

```
Viewcount.objects.popular(7, 300)
```

**Important** - The list of page IDs that comes back is built purely from the view_counts table, so it's then up to you to check that those pages are live etc.

If for some reason you want the counts as well as the page IDs, you can call

```
ViewCount.objects.popular_with_counts()
```

