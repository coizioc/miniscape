with open('itemconsts.txt', 'r') as f:
    items = f.read().split('\n')

with open('itemconsts.py', 'w+') as f:
    f.write("from miniscape.models import Item\n\n")
    for item in sorted(items):
        var_name = item.upper().replace(' ', '_').replace('\'', '')
        s = f"{var_name} = Item.objects.get(name__iexact=\'{item}\')\n"
        f.write(s)
