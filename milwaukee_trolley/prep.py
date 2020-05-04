import psycopg2 as pg
import geopandas as gp

if __name__ == "__main__":
    with pg.connect(host='localhost', dbname='mcanearm', user='mcanearm', port=5432) as conn:
        trolley_routes = gp.read_postgis(
            sql="select * from trolley_routes_26916 where year = '1938'", con=conn, geom_col='geom'
        )
        bus_routes = gp.read_postgis(sql='select * from bus_routes_26916', con=conn, geom_col='geom')
        blocks = gp.read_postgis(sql='select * from milwaukee_census_blocks', con=conn, geom_col='geom')

    """
    Steven Manson, Jonathan Schroeder, David Van Riper, and Steven Ruggles. 
    IPUMS National Historical Geographic Information System: Version 14.0 [Database]. 
    Minneapolis, MN: IPUMS. 2019. http://doi.org/10.18128/D050.V14.0
    """

    trolley_routes['geom'] = trolley_routes.buffer(1000)
    bus_routes['geom'] = bus_routes.buffer(1000)

    # For each route, identify each block served along with its population and housing count
    trolley_blocks = gp.sjoin(blocks, trolley_routes, how='inner', op='intersects')[
        ['gid', 'housing10', 'pop10', 'geom', 'route_id']]. \
        drop_duplicates()

    # Do the same for buses.
    bus_blocks = gp.sjoin(blocks, bus_routes, how='inner', op='intersects')[
        ['gid_left', 'housing10', 'pop10', 'geom', 'gid_right']]. \
        drop_duplicates()

    with open('./data/paper-data/trolley_blocks.csv', 'w') as f:
        trolley_blocks.to_csv(f)
    with open('./data/paper-data/bus_blocks.csv', 'w') as f:
        bus_blocks.to_csv(f)

    # population served in total
    # trolley_blocks[['housing10', 'pop10']].sum()
    # bus_blocks[['housing10', 'pop10']].sum()
    #
    # # population served by each route
    # trolley_route_service = trolley_blocks.groupby('id_right')[['housing10', 'pop10']].sum().sort_values('pop10')
    # bus_route_service = bus_blocks.groupby('id_right')[['housing10', 'pop10']].sum().sort_values('pop10')
    #
    # trolley_route_service['id_pct'] = (np.array(range(trolley_route_service.shape[0])) + 1) / trolley_route_service.shape[0]
    # bus_route_service['id_pct'] = (np.array(range(bus_route_service.shape[0])) + 1) / bus_route_service.shape[0]
    #
    # trolley_route_service['pop10_pct'] = trolley_route_service['pop10'].cumsum() / trolley_route_service['pop10'].sum()
    # bus_route_service['pop10_pct'] = bus_route_service['pop10'].cumsum() / bus_route_service['pop10'].sum()
    #
    # allRoutes = pd.concat([trolley_route_service, bus_route_service], keys=['trolley', 'bus'], names=['Route Type']). \
    #     reset_index(). \
    #     set_index('Route Type')
    #
    # fig, ax = pyplot.subplots(figsize=(8, 6))
    # allRoutes.groupby('Route Type')['id_pct', 'pop10_pct'].plot(x='id_pct', y='pop10_pct', kind='line', ax=ax)
    # pyplot.show()
