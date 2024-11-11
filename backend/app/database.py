import sys, os, configparser, pyodbc
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Union
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

config = configparser.ConfigParser()
config_file = BASE_DIR / 'config.ini'
if os.path.exists(config_file):
    config.read(config_file, encoding='utf-8')
else:
    print("error! config file doesn't exist"); sys.exit()


DB_CONNECTION_STRING = config['db']['db_connection_string']
DB_NAME = config['db']['db_name']
DB_SCHEMA = config['db']['db_schema']
COMPANY_NAME = config['content']['company_name']


class Database(ABC):
    """
    Database context manager
    """

    def __init__(self, driver) -> None:
        self.driver = driver

    @abstractmethod
    def connect_to_database(self):
        raise NotImplementedError()
    
    def __enter__(self):
        self.connection = self.connect_to_database()
        self.cursor = self.connection.cursor()
        return self
    
    def __exit__(self, exception_type, exc_val, traceback):
        self.cursor.close()
        self.connection.close()


class DBConnect(Database):
    """PyODBC Database context manager"""

    def __init__(self) -> None:
        self.driver = pyodbc
        super().__init__(self.driver)

    def connect_to_database(self):
        return self.driver.connect(DB_CONNECTION_STRING)


select = {}

select['product_quantity'] = f"""
  SELECT count(*) product_quantity FROM {DB_NAME}.{DB_SCHEMA}.tovar_sklad
"""

select['dt_quantity'] = f"""
  SELECT count(*) dt_quantity FROM (SELECT id_doc FROM {DB_NAME}.{DB_SCHEMA}.tovar_sklad GROUP BY id_doc) AS a
"""

select['tnved_quantity'] = f"""
            select * from (
            SELECT TOP 7 * FROM
                (SELECT LEFT(g33_in,4) g33, count(*) cnt
                FROM {DB_NAME}.{DB_SCHEMA}.tovar_sklad  WHERE 1=1
                GROUP BY LEFT(g33_in,4)) AS a
                ORDER BY 2 DESC) b
                order by cnt desc
        """

select['products_on_storage'] = f"""
  SELECT id,gtdnum,name, cast(date_in as date) date_in, g32,g31,g33_in,g31_2,
  CASE WHEN g41a <>'166' THEN g31_3 ELSE 0 END g31_3,
  CASE WHEN g41a <>'166' THEN g31_3a ELSE '' END g31_3a,
  g35,g41a, cast(date_chk as date) date_chk, country 
  FROM {DB_NAME}.{DB_SCHEMA}.TOVAR_SKLAD 
  ORDER BY date_in ASC,gtdnum,g32
"""

#########################
filter_string_mark = '!filter_string_mark!'

select['received_product_quantity'] = f"""
  SELECT count(*) received_product_quantity
    FROM {DB_NAME}.{DB_SCHEMA}.doc_in_sklad d, {DB_NAME}.{DB_SCHEMA}.doc_in_sklad_sub s 
    WHERE s.main_id=d.id AND d.posted > 0
    {filter_string_mark}
    
"""
# {dashboard_filter_string}
# select_filter[s5] = list()
# select_filter[s5].append("and d.date_doc >='dashboard_filter_0_0'")
# select_filter[s5].append("and d.date_doc <= 'dashboard_filter_0_1'")


select['received_dt_quantity'] = f"""
  SELECT count(*) received_dt_quantity
    FROM {DB_NAME}.{DB_SCHEMA}.doc_in_sklad d
    WHERE posted > 0
    {filter_string_mark}
"""
# {dashboard_filter_string}
# select_filter[s6] = list()
# select_filter[s6].append("and d.date_doc >='dashboard_filter_0_0'")
# select_filter[s6].append("and d.date_doc <= 'dashboard_filter_0_1'")


select['received_tnved_quantity'] = f"""
  SELECT TOP 7 * FROM
  (SELECT  LEFT(s.g33_in,4) g33, count(*) cnt 
    FROM {DB_NAME}.{DB_SCHEMA}.doc_in_sklad_sub s, {DB_NAME}.{DB_SCHEMA}.doc_in_sklad d  
    where s.main_id=d.id AND d.posted > 0
    {filter_string_mark}
    GROUP BY LEFT(s.g33_in,4)) AS a
  ORDER BY 2 DESC
"""
# select_filter[s7] = list()
# select_filter[s7].append("and d.date_doc >='dashboard_filter_0_0'")
# select_filter[s7].append("and d.date_doc <= 'dashboard_filter_0_1'")


select['account_book'] = f"""
  SELECT * FROM 
  (SELECT UniqueIndexField as id, id as id_0, f_p,name,gtdnum, cast(date_in as date) date_in, time_in,
  cast(date_otc as date) date_otc, cast(date_chk as date) date_chk, g32,g31,g33_in,g35,
  CASE WHEN g31_3a <>'КГ' THEN g31_3 ELSE 0 END g31_3,
  CASE WHEN g31_3a <>'КГ' THEN g31_3a ELSE '' END g31_3a,
  doc_num_out, gtdregime_out, cast(date_out as date) date_out, g32_out, g33_out, g31_2_out, g35_out,
  CASE WHEN g31_3a <>'КГ' THEN g31_3_out ELSE 0 END g31_3_out
  FROM {DB_NAME}.{DB_SCHEMA}.jr_sklad ) AS a
  where 1=1
  {filter_string_mark}
  ORDER BY date_in,id ASC,g32 ASC,f_p DESC,date_otc ASC
"""
# select_filter[s8] = list()
# select_filter[s8].append("and date_in >='dashboard_filter_1_0'")
# select_filter[s8].append("and date_in <= 'dashboard_filter_1_1'")


# select['report_vehicle'] = f"""
# SELECT nn as id, gtdnum,g32,g33_in,g31,
# CAST(g35 AS NUMERIC(18,3)) g35,
# g31_3a,place,gtdregime_out,doc_num_out,g33_out,
# CAST(g35_out AS NUMERIC(18,3)) g35_out,
# CASE WHEN g31_3a <> 'КГ' THEN CAST(CAST(g31_3 AS NUMERIC(18,3)) AS VARCHAR)+'/'+g31_3a ELSE '0' END g31_3, 
# CASE WHEN g31_3a <> 'КГ' THEN CAST(CAST(g31_3_out AS NUMERIC(18,3)) AS VARCHAR)+'/'+g31_3a ELSE '0' END g31_3_out, 
# CONVERT(VARCHAR,date_in,105) AS date_in,
# CONVERT(VARCHAR,date_chk,105) AS date_chk,
# CASE WHEN exp_date IS NOT NULL THEN CONVERT(VARCHAR,exp_date,105) ELSE 'ОТСУТСТВУЕТ' END AS exp_date,
# CONVERT(VARCHAR,date_out,105) AS date_out,
# CASE WHEN g31_3ost>0 THEN CAST(g35ost AS NUMERIC(18,3)) ELSE 0 END g35ost_,
# CASE WHEN g31_3a <> 'КГ' THEN CAST(CAST(g31_3ost AS NUMERIC(18,3)) AS VARCHAR)+'/'+g31_3a ELSE '0' END g31_3ost_ 
# FROM (SELECT CONVERT(INTEGER,row_number() OVER( ORDER BY j.date_in,j.id,j.g32,j.key_id,jj.date_out)) nn,j.*,
#    jj.date_out,jj.doc_num_out,jj.gtdregime_out,
#    jj.g35_out,jj.g31_3_out,jj.g31_3a_out,jj.g31_out,jj.g32_out,jj.g33_out,j.g31_3-ISNULL(jjj.g31_3sout,0) g31_3ost,
#    g35-ISNULL(jjj.g35sout,0) g35ost 
# FROM (SELECT j.id,j.key_id,j.g32,j.gtdnum,j.date_in,j.g31,j.g31_3,j.g31_3a,j.g33_in,j.g35,j.gtdregime_in,j.date_chk,
#    j.place,s.exp_date,s.g41a_dt,u.code 
# FROM ({DB_NAME}.{DB_SCHEMA}.jr_sklad j LEFT OUTER JOIN {DB_NAME}.{DB_SCHEMA}.units u ON u.name10=j.g31_3a) 
# LEFT OUTER JOIN {DB_NAME}.{DB_SCHEMA}.doc_in_sklad_sub s ON s.key_id=j.key_id 
# WHERE f_p='1' 
# {filter_string_mark}
# ) 
# j LEFT OUTER JOIN (SELECT key_id,sum(g35_out) 
#    g35sout,sum(g31_3_out) g31_3sout 
# FROM {DB_NAME}.{DB_SCHEMA}.jr_sklad jj WHERE f_p='0' GROUP BY key_id ) jjj ON jjj.key_id=j.key_id 
# LEFT OUTER JOIN (SELECT key_id,doc_num_out,gtdregime_out,date_out,g31_3_out,g31_3a_out,g35_out,g31_out,g32_out,g33_out 
# FROM {DB_NAME}.{DB_SCHEMA}.jr_sklad WHERE  f_p='0') jj  ON j.key_id=jj.key_id ) AS a WHERE 1=1
# ORDER BY nn
# """
# select_filter[s9] = list()
# select_filter[s9].append("and date_out >='dashboard_filter_2_0'")
# select_filter[s9].append("and date_in <= 'dashboard_filter_2_1'")


def create_select(select, select_name, filters):
    #
    if not filters:
        return select[select_name].replace(filter_string_mark, '')

    filter_substring = str()

    # and d.date_doc >='dashboard_filter_0_0' and d.date_doc <= 'dashboard_filter_0_1'
    if select_name in ['received_product_quantity', 'received_dt_quantity', 'received_tnved_quantity']:
        if filters['filterAccountBookDateDocFrom']:
            filter_substring += f"and d.date_doc >='{filters['filterAccountBookDateDocFrom'].replace('-', '')}'"
        if filters['filterAccountBookDateDocTo']:
            filter_substring += f"and d.date_doc <='{filters['filterAccountBookDateDocTo'].replace('-', '')}'"

    # and date_in >='dashboard_filter_1_0' and date_in <= 'dashboard_filter_1_1'
    if select_name in ['account_book']:
        if filters['filterAccountBookDateEnterFrom']:
            filter_substring += f"and date_in >='{filters['filterAccountBookDateEnterFrom'].replace('-', '')}'"
        if filters['filterAccountBookDateEnterTo']:
            filter_substring += f"and date_in <='{filters['filterAccountBookDateEnterTo'].replace('-', '')}'"

    # and date_out >='dashboard_filter_2_0' and date_in <= 'dashboard_filter_2_1'
    if select_name in ['report_vehicle']:
        if filters['filterReportVehicleDateEnterFrom']:
            filter_substring += f"and date_out >='{filters['filterReportVehicleDateEnterFrom'].replace('-', '')}'"
        if filters['filterReportVehicleDateExitTo']:
            filter_substring += f"and date_in <='{filters['filterReportVehicleDateExitTo'].replace('-', '')}'"

    sql_query = select[select_name].replace(filter_string_mark, filter_substring)
    
    return sql_query



def select_widget_data(select_name, filters):
    #
    with DBConnect() as db:

        query = create_select(select, select_name, filters)
        db.cursor.execute(query)

        # print('description =', db.cursor.description)
        dataset_columns_info = [ (i[0], i[1]) for i in db.cursor.description ]
        # print('dataset_columns_info =', dataset_columns_info)


        dataset = db.cursor.fetchall()
        #print('dataset =', dataset) #

        objects = []
        for data in dataset:

            item = {}
            for i in range(len(dataset_columns_info)):
                item[dataset_columns_info[i][0]] = data[i]
            
            objects.append(item)

        # objects = [
        #     {   
        #         "g33": data[0],
        #         "cnt": data[1],
        #     }
        #     for data in dataset
        # ]

        # print('obj_list =', obj_list)
        # print('objects =', objects)
        
    return objects    


def select_dashboard_data(selects_keys_list=select, filters:Union[dict, None]=None):
    # with DBConnect() as db:
    #     query = """
    #         select * from (
    #         SELECT TOP 7 * FROM
    #             (SELECT LEFT(g33_in,4) g33, count(*) cnt
    #             FROM Luding.dbo.tovar_sklad  WHERE 1=1
    #             GROUP BY LEFT(g33_in,4)) AS a
    #             ORDER BY 2 DESC) b
    #             order by cnt
    #     """
    #     db.cursor.execute(query)
    #     objects = [
    #         {   
    #             "g33": data[0],
    #             "cnt": data[1],
    #         }
    #         for data in db.cursor.fetchall()
    #     ]
    # print('filters = ', filters)

    objects = {}
    for s in selects_keys_list:
        # objects = {'tnved_quantity': select_widget_data('tnved_quantity')}
        objects[s] = select_widget_data(s, filters)
        
    objects['company_name'] = COMPANY_NAME
    objects['current_datetime'] = datetime.now().strftime("%d-%m-%Y %H:%M")

    return objects


#################

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from urllib.parse import quote_plus

#SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
SQLALCHEMY_DATABASE_URL = f'postgresql://postgres:%s@localhost/dev_pg_2' % quote_plus('s2d3f4!@')
# SQLALCHEMY_DATABASE_URL = 'mssql+pyodbc://' + 'LAPTOP-MR8NJ1DK\SQLEXPRESS' + '/' + 'dev_db_1' + '?trusted_connection=yes&encrypt=no&driver=ODBC+Driver+18+for+SQL+Server'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # connect_args={"check_same_thread": False} # for sqlite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
