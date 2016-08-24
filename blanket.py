import click
import duvet

@click.command()
@click.option('--search', prompt='Search String', help='What would you like to search for?')
@click.option('--season', default=None, help="Season Number.", type=click.INT)
@click.option('--episode', default=None, help="Episode Number.", type=click.INT)
@click.option('--min-seeders', default=100, help="Minimum number of seeders.")
@click.option('--show', default=5, help="How many results to show.")
def execute_search(search, season, episode, min_seeders, show):
    d = duvet.Duvet()
    results = d.search(search, season=season, episode=episode, min_seeders=min_seeders)
    for r in results[0:show]:
        print(r)
        print(r.magnet)
        print("")

if __name__ == '__main__':
    execute_search()
