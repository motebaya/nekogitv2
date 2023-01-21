#!/usr/bin/env python3

from nekov2 import NekoV2

def save(f, to):
    with open(to, 'w') as w:
        w.write(f)

# sample call
h = list(NekoV2().get_hentai_list())
save(str(h), 'test/all_hentai_list.json')
h = NekoV2().get_hentai_info(h[0])
save(str(h), 'test/hentai_info.json')
h = NekoV2().get_download(
    h['eps'][0]['1']
)
save(str(h), 'test/download.json')

h = NekoV2().bypass_ouo("https://ouo.io/hGaEhd")
print(h)