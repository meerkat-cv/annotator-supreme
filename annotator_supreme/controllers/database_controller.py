import os
from annotator_supreme import app
import cassandra
from cassandra.cluster import Cluster
from annotator_supreme.models import bbox_model
# from annotator_supreme.models import image_model

db_global = None

def get_db(config):
    """
    This functions connect to the Cassandra database and kept in the flask app
    """
    KEYSPACE = app.config["KEYSPACE"]
    CLUSTER_IP = app.config["CLUSTER_IP"]

    global db_global
    with app.app_context():
        if db_global is None:
            app.logger.info("database connection done again with ip: %s",CLUSTER_IP)
            cluster = Cluster([ CLUSTER_IP ], connect_timeout=1000)
            
            session = cluster.connect(KEYSPACE)
            session.default_timeout = 100
            db_global = session

        return db_global

class DatabaseController:

    def setup_database(self):
        KEYSPACE = app.config["KEYSPACE"]
        CLUSTER_IP = app.config["CLUSTER_IP"]
        
        cluster = Cluster([ CLUSTER_IP ], protocol_version=3)
          
        session = cluster.connect()

        # first create the database (aka keyspace)
        try:
            session.execute("""
                CREATE KEYSPACE %s
                WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
                """ % KEYSPACE)
        except cassandra.AlreadyExists:
            app.logger.info("Keyspace already exists.")

        # redefine session to use the keyspace
        session.set_keyspace(KEYSPACE)

        try:
            app.logger.info("\t- creating table dataset")
            session.execute("""
                CREATE TABLE datasets (
                    name text PRIMARY KEY,
                    tags list<text>,
                    annotation_labels list<text>,
                    image_categories list<text>,
                    last_modified timestamp
                )
                """)
        except cassandra.AlreadyExists:
            app.logger.info("Table 'datasets' already exists.")


        app.logger.info("\t- creating type bbox")
        session.execute("""
            CREATE TYPE IF NOT EXISTS bbox (
                labels list<text>,
                top float,
                left float,
                bottom float,
                right float,
                ignore boolean
            )
            """)

        # cluster.register_user_type(KEYSPACE, 'bbox', bbox_model.BBox)

        try:
            app.logger.info("\t- creating table images")
            session.execute("""
                CREATE TABLE images (
                    phash text,
                    dataset text,
                    name text,
                    img blob,
                    width int,
                    height int,
                    category text,
                    partition int,
                    fold int,
                    last_modified timestamp,
                    annotation frozen<list<bbox>>,
                    PRIMARY KEY ((dataset), phash)
                )
                """)
        except cassandra.AlreadyExists:
            app.logger.info("Table 'images' already exists.")


        try:
            app.logger.info("\t- creating table images_img")
            session.execute("""
                CREATE TABLE images_img (
                    phash text,
                    img blob,
                    PRIMARY KEY (phash)
                )
                """)
        except cassandra.AlreadyExists:
            app.logger.info("Table 'images_img' already exists.")


        try:
            app.logger.info("\t- creating table label_ref_count")
            session.execute("""
                CREATE TABLE label_ref_count (
                    dataset text,
                    label text,
                    ref_count int,
                    PRIMARY KEY ((dataset), label)
                )
                """)
        except cassandra.AlreadyExists:
            app.logger.info("Table 'label_ref_count' already exists.")


        try:
            app.logger.info("\t- creating table category_ref_count")
            session.execute("""
                CREATE TABLE category_ref_count (
                    dataset text,
                    category text,
                    ref_count int,
                    PRIMARY KEY ((dataset), category)
                )
                """)
        except cassandra.AlreadyExists:
            app.logger.info("Table 'category_ref_count' already exists.")

        try:
            app.logger.info("\t- creating table users")
            session.execute("""
                CREATE TABLE users (
                    username text,
                    password_hash text,
                    email text,
                    registration_date timestamp,
                    PRIMARY KEY (username)
                )
                """)
        except cassandra.AlreadyExists:
            app.logger.info("Table 'users' already exists.")

