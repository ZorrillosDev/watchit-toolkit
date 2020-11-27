import requests
from contextlib import contextmanager
from multiprocessing import Pool

from resource.py import Log
from resource.py.media.ingest import download_file, ingest_dir, get_pb_domain_set

__author__ = 'gmena'


class YTS(object):
    def __init__(self, host: str, page: int = 0, limit: int = 50):
        # ignore 400 cause by IndexAlreadyExistsException when creating an index

        # CONSTANTS
        self.YTS_HOST = host
        self.YTS_RECURSIVE_LIMIT = limit  # limit result per page (step)

        self.yts_recursive_page = page  # start page
        self.yts_movies_indexed = dict()  # indexed
        self.req_session = requests.Session()
        self.pb_match = get_pb_domain_set()

    @contextmanager
    def request(self, query_string=None):
        """
        Handle http request
        :param query_string:
        :return:
        """
        # Request yifi
        _request: str = self.YTS_HOST + ('?%s' % query_string if query_string else '')
        _cookie = '__cfduid=d69cbd9b1eab1aac23ce5bdf7b56d617e1605989262; adcashufpv3=17981512371092097718392042062; PHPSESSID=algs7ie2teub9v8ebpeg5rrrp9; __atuvc=1%7C47%2C3%7C48'
        _agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'

        try:
            conn = self.req_session.get(
                url=_request,
                timeout=60,
                headers={
                    "content-type": "json",
                    'user-agent': _agent,
                    'cookie': _cookie
                }
            )

            # Return json
            yield conn.json()
        except (Exception,) as e:
            print(e)
            yield {}

    def get_movies(self, page):
        # Req YTS
        print(f"Requesting page {str(page)}")
        _uri = 'page=' + str(page) + '&limit=' + str(self.YTS_RECURSIVE_LIMIT) + '&sort=date_added'
        with self.request(_uri) as conn_result:
            # OK 200?
            if 'status' in conn_result and conn_result['status'] != 'ok':
                return False
            if 'movies' not in conn_result['data']:
                return False
            # Yield result
            return conn_result['data']['movies']

    def request_generator(self) -> iter:
        """
        Request yts handler
        :return:
        """

        # Uri
        with self.request() as ping:
            if not 'data' in ping: return False
            total_pages = round(int(ping['data']['movie_count']) / self.YTS_RECURSIVE_LIMIT)
            total_pages = total_pages if self.yts_recursive_page == 0 else self.yts_recursive_page

            print(f"{Log.HEADER}Requesting {str(total_pages)} pages {Log.ENDC}")
            page_list = range(total_pages)

            with Pool(processes=10) as pool:
                p_async = pool.apply_async
                results = {}

                # Generate async pools
                for x in page_list:
                    results[x] = p_async(
                        self.get_movies, args=(x,)
                    )

                # Close pool
                pool.close()
                pool.join()
            # Generate dict with data
            for x, y in results.items():
                yield x, y.get()

    def ingest_media(self, mv):
        print(f"\n{Log.OKBLUE}Ingesting {mv['imdb_code']}{Log.ENDC}")
        # Downloading files
        current_imdb_code = mv['imdb_code']
        current_imdb_code_set = set(current_imdb_code)
        public_domain_movie = self.pb_match.intersection(current_imdb_code_set)

        image_index = [
            "background_image", "background_image_original",
            "small_cover_image", "medium_cover_image", "large_cover_image"
        ]

        for x in image_index:  # Download all image assets
            download_file(mv[x], "%s/%s.jpg" % (current_imdb_code, x))
            del mv[x]

        for torrent in mv['torrents']:
            torrent_dir = '%s/%s/%s' % (current_imdb_code, torrent['quality'], torrent['hash'])
            download_file(torrent['url'], torrent_dir)

        del mv['torrents']
        hash_directory = ingest_dir(current_imdb_code)
        mv['hash'] = hash_directory
        mv['pdm'] = bool(public_domain_movie)

        # Logs on ready ingested
        print(f"Public domain movie? {Log.BOLD}{bool(public_domain_movie)}{Log.ENDC}")
        print(f"Hash ready for {current_imdb_code}: {hash_directory}")
        print(f"{Log.OKGREEN}Done {mv['imdb_code']}{Log.ENDC}\n")
        return mv

    def process_ingestion(self,yts_movies_indexed):
        with Pool(processes=2) as pool:
            p_async = pool.apply_async
            results = {x: p_async(  # Pool process ingest
                self.ingest_media, args=(yts_movies_indexed[x],)
            ) for x in yts_movies_indexed}

            pool.close()
            pool.join()

            return {  # Generate ingestion dict
                x: y.get() for x, y in results.items()
            }

    @contextmanager
    def migrate(self, resource_name: str):
        """
        Elastic migrate
        :param resource_name:
        :return:
        """
        # Get generator
        for page, movie_meta_iter in self.request_generator():
            if movie_meta_iter:
                for movie_meta in movie_meta_iter:
                    print('indexing ' + movie_meta['title'])
                    # Rewrite resource id
                    movie_meta['page'] = page
                    movie_meta['resource_id'] = movie_meta['id']
                    movie_meta['resource_name'] = resource_name
                    movie_meta['trailer_code'] = movie_meta['yt_trailer_code']

                    del movie_meta['yt_trailer_code']
                    del movie_meta['id']
                    del movie_meta['state']
                    del movie_meta['url']
                    # Push indexed movie
                    self.yts_movies_indexed[
                        movie_meta['imdb_code']
                    ] = movie_meta

        # Return result
        return self.process_ingestion(
            self.yts_movies_indexed
        )
