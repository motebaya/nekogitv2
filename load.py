#!/usr/bin/env python3

from rich import print as rich_print
from rich.tree import Tree
from rich import box
from rich.table import Table
from rich.prompt import Prompt, Confirm
from os import listdir, mkdir as makedir
from os.path import exists as path_exists
from nekov2 import json, ctime, NekoV2, requests, sys

def Load_db(dir: str ="./database"):
	if path_exists(dir):
		for file in listdir(dir):
			yield {file.split(".")[0]: open(
				f"{dir}/{file}"
			).read(
		).strip()}
	return None

def show_tree(lists: list, search: str = ''):
	results = []
	if not search:
		tree = Tree("[green] All Hentai List[white]: ")
	else:
		rich_print(f"Searching: [green]{search}[white]")
	
	t = 1
	for v in lists:
		data = list(v.values())[0].splitlines()
		if not search:
			tree_value = Tree("[red]{}[white]: ([bright_yellow]{}[white])".format(
				list(v.keys())[0], len(data)
			))
		for dat in data:
			j = json.loads(dat)
			if str(search).strip():
				if str(search).lower() in j['title'].lower():
					results.append(j)
					t += 1
				else:
					continue
			else:
				tree_value.add("[green]{}[white]). {}".format(
					t, j['title']
				))
				t += 1
		if not search:
			tree.add(tree_value)
	if not search:
		rich_print(tree)
	return results

def _prompt(menu: list):
	if menu:
		choice = Prompt.ask(
			"[green] Choice", choices=list(map(
				str, list(
					range(1, len(menu) + 1)
				)
			)
		))
	else:
		while True:
			choice = Prompt.ask(
				"\n[yellow] Set"
			)
			if not choice.strip(): # and choice.isdigit():
				rich_print(
					"[red] please input a value![white]"
				)
				continue
			else:
				break

	return int(choice
		) if choice.isdigit(
			) else choice

def show_box(title: str, menu: list, prompt_=False, _tree=False):
	if not _tree:
		table = Table(
			box=box.SQUARE,
			title=title,
			title_justify="center"
		)
		table.add_column(
			title.title() + ": by motebaya" if title.isalpha(
				) else "Menu: by motebaya",
			justify="left",style="cyan")
		for k, v in enumerate(menu, 1):
			if prompt_:
				table.add_row(
					f"[green] {k}[white]). {v}"
				)
			else:
				table.add_row(
					f"[white] ↦ {v[0].title()}:[green]{v[1]}"
				)
		rich_print(table)
	if prompt_:
		return _prompt(
			menu
		)

def get_valid_json(l: list):
	for j, k in enumerate(l, 1):
		data = list(k.values())[0].splitlines()
		for l in data:
			yield json.loads(l)

def handle(res: list, s: bool = False):
	if len(res) != 0:
		c = res[show_box(
			"results",
			list(map(
				lambda x: x['title'].title(), res
			)),
			True,
			s
		) - 1]
		eps = c.get('eps')
		c.pop('eps')
		show_box(
			"Info",
			list(c.items())
		)

		e = eps[show_box(
			"List Episode:",
			list(map(
				lambda x: f"Episode {x[0]}", enumerate(
			eps, 1))),
			True
		) - 1]['link']

		q = list(e[show_box(
			"Quality List",
			list(map(
				lambda x: list(
					x.keys())[0], e)),
			True
		) - 1].values())[0]

		dl = show_box(
			"Download Link",
			list(map(
				lambda x: ': '.join(
					list(x.items())[0]), q)),
			True
		)

		link = list(q[dl - 1].values())[0]
		if "ouo.io" in link:
			link = NekoV2().bypass_ouo(link)
		rich_print(f"[green] URL: [yellow] -> {link}[white]")
		print()
		main()
	else:
		rich_print("[red] Empty REsults!")
		main()

def save_data(inf: dict):
	if not path_exists("./database"):
		makedir("./database")
	info = NekoV2().get_hentai_info(inf)
	for en, dl in enumerate(info["eps"], 1):
		eps = NekoV2().get_download(
			dl[str(en)])
		info['eps'][en-1]['link'] = eps
		NekoV2().debug(
			f"ok with {len(eps)} server")
	filename = "./database/{}.json".format(info['title'].upper()[0])
	with open(filename, "a") as f:
		f.write(
			json.dumps(info) + "\n"
		)
	NekoV2().debug(
		f"saved to : ``{filename}``")
	return info

def main():
	choice = show_box("╔╗╔┌─┐┬┌─┌─┐╔═╗┌─┐╦\n║║║├┤ ├┴┐│ │╠═╝│ │║\n   ╝╚╝└─┘┴ ┴└─┘╩  └─┘╩v2", [
		"search title fom list",
		"quick choice from list",
		"check update from site",
		"get all list from site",
	], True)
	list_hentai = list(Load_db())
	if choice in range(1, 4):
		if list_hentai:
			if choice == 1:
				handle(show_tree(
					list_hentai,
					_prompt([])
				))
			elif choice == 2:
				show_tree(list_hentai)
				handle(list(
					get_valid_json(list_hentai)),
					True
				)
			elif choice == 3:
				try:
					hentai = list(NekoV2().get_hentai_list(
						))
				except Exception as e:
					if "CertificateError" in str(e):
						requests.warnings.warn("\033[1;31mu need vpn to run it")
					exit(str(e))

				if hentai:
					load_title = list(map(
						lambda x: x.get('id'),
						list(get_valid_json(
							list(
								Load_db()
							)
						))
					))
					t = 1
					for k, h in enumerate(hentai, 1):
						sys.stdout.write(
							f"\r![{NekoV2().get_time()}]\033[37m Checking Update: \033[32m{k} \033[37mof \033[33m{len(hentai)}\033[0m")
						sys.stdout.flush()
						if h.get('id') not in load_title:
							NekoV2().debug(
								f"\n({t}) new update :{h.get('title')}"
							)
							save_data(h)
							t += 1
						else:
							continue
					if t == 1:
						NekoV2().debug(
							"Nothing, all up to date!"
						)
						exit()
					else:
						rich_print(
							f"\n[green] success update, new: [yellow]{t}"
						)
						exit()
				else:
					requests.warnings.warn("\033[1;31mEMpty REsult from list!")
		else:
			rich_print("[red] u doon't have [green] folder!")
			exit()
	else:
		if choice == 4:
			if list(Load_db()):
				requests.warnings.warn(
					"u already have `database` list!"
				)
				if not Confirm.ask("[green] Reset?"):
					main()
			try:
				hentai = list(NekoV2(
					).get_hentai_list(
				))
				if hentai:
					NekoV2().debug(
						f"ok with total list: {str(len(hentai))}")
					for x, y in enumerate(hentai, 1):
						NekoV2().debug("process: {} of {}".format(
							str(+x), str(len(hentai))
						))
						save_data(y)
				else:
					requests.warnings.warn(
						"Nothing results !"
					)
					exit()
			except Exception as e:
				if "CertificateError" in str(e):
					requests.warnings.warn("\033[1;31mu need vpn to run it")
				exit(str(e))

if __name__=="__main__":
	main()