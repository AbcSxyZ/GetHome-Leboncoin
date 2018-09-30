def print_urls(urls_list, file):
    with open(file, 'w') as File:
        for url in urls_list:
            print(url, file=File)

def id_to_url(file):
    with open(file, 'r') as url_file:
        content = url_file.read()
        ids = content.split('\n')
        ids = list(filter(None, ids))
        url_format = "https://www.leboncoin.fr/colocations/{}.htm/"
        urls_list = [url_format.format(id_elem) for id_elem in ids]
    return urls_list


def print_links(link_list, file):
    id_list = []
    for link in link_list:
        link_id = link.split('/')[-2]
        link_id = link_id.replace('.htm', '')
        id_list.append(link_id)

    id_list = [int(id_x) for id_x in id_list]
    id_list.sort()
    new_file = open(file, "w")
    for id_elem in id_list:
        print(id_elem, file=new_file)
    new_file.close()
