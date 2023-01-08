### NekopoiV2

<p align="center">
	<img src="images/20230108_134359.png">
</p>

<sub><sup>[source](https://www.deviantart.com/nephi-chanmoe/art/NekoPoi-Logo-874921085)</sup></sub>

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

### Menu

```
      ╔╗╔┌─┐┬┌─┌─┐╔═╗┌─┐╦
      ║║║├┤ ├┴┐│ │╠═╝│ │║
      ╝╚╝└─┘┴ ┴└─┘╩  └─┘╩v2
┌─────────────────────────────┐
│ Menu: by motebaya           │
├─────────────────────────────┤
│  1). search title fom list  │
│  2). quick choice from list │
│  3). check update from site │
│  4). get all list from site │
└─────────────────────────────┘
 Choice [1/2/3/4]:
```
