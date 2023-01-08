## NekopoiV2

<p align="center">
	<img width="37%" height="37%" src="images/20230108_134359.png">
</p>

<sub><sup>[source](https://www.deviantart.com/nephi-chanmoe/art/NekoPoi-Logo-874921085)</sup></sub>

![](https://img.shields.io/badge/Python-3.10-blue)

-   get hanime list:

```
list(NekoV2().get_hentai_list())
```

-   get hanime info:

```
@param: dict
NekoV2().get_hentai_info(
	{"title": <title>, "id": <id>}
)
```

-   get episode list

```
@param: str
NekoV2().get_download(
	info['eps'][<index>][<eps>]
)
```

## Menu


- [x] search title fom list
- [x] quick choice from list
- [x] check update from site
- [x] get all list from site
