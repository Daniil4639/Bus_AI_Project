from datetime import datetime

import cv2

from .db_utils import *

class PostgresDbConnector(object):

    def __init__(self):
        self.engine = get_engine_from_settings()
        self.connection = self.engine.connect()

        self.metadata = sa.MetaData()
        self.log_table = sa.Table(
            'warning_logs',
            self.metadata,
            sa.Column('id', sa.INTEGER, primary_key=True, autoincrement=True),
            sa.Column('time', sa.DateTime, default=datetime.now(), nullable=False),
            sa.Column('warning_messages', sa.String, nullable=False),
            sa.Column('image', sa.LargeBinary, nullable=True)
        )

        self.metadata.create_all(self.engine)

    def insert_warnings(self, warnings, image):
        resized_image = resize_image(image)

        new_log_query = self.log_table.insert().values(
            warning_messages=str(warnings),
            image=encode_image(resized_image)
        )
        self.connection.execute(new_log_query)
        self.connection.commit()

    # Сугубо для демонстрации
    def get_warnings(self, row_id):
        log_data_query = sa.select(self.log_table).where(self.log_table.c.id == row_id)
        result = self.connection.execute(log_data_query).fetchone()

        print(result[0])
        print(result[1])
        print(result[2])
        if result[3] is not None:
            cv2.imshow('img', decode_image(result[3]))
            cv2.waitKey(0)
