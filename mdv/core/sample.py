'''
Generate a markdown sample.
'''


def make_sample(admons):
    """ Generate the theme roller sample markdown """

    headers = ['#' * hl + ' ' + 'Header %s' % hl for hl in range(1, 7)]

    this = open(__file__).read().split('"""', 3)[2].splitlines()[:10]
    code = ['''```python
    """ Test """
    {code}
```'''.format(code='\n'.join(this))]

    table = ["""
| Tables        | Fmt | Rest |
| -- | -- | -- |
| !!! hint: wrapped | 0.1 **strong** | ... |
    """]

    admonitions = ['!!! %s: title\n    this is a %s\n' % (ad, ad.capitalize())
                   for ad in admons.keys()]

    you_like = 'You like this theme?'
    like = ['\n----\n!!! question: %s' % you_like]

    print('[warning]', 'uncomment the line below!')
    return '\n\n'.join(headers + code + table + admonitions + like)
