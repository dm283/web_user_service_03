endpoint_allowed_roles_dict = {
    'put'+'upload_file': ['admin',],
    'put'+'/upload_excel_list/': ['admin',],
    'put'+'/upload_file_for_carpass/': ['ALL', ],
    'get'+'log_records': ['admin',],
    'get'+'tcell': ['admin', 'dispatcher'],
    'get'+'download_carpass': ['admin', 'dispatcher'],
    'get'+'download-file-by-filename': ['admin', 'dispatcher'],
    'post'+'create_related_docs_record': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker',],
    'get'+'download-file': ['admin','client','broker'],
    'get'+'obj_docs': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],

    # users
    'get'+'users': ['admin',],
    # user card
    'get'+'roles': ['admin',],
    'get'+'partners_posted': ['admin',],
    'get'+'role': ['admin',],
    'put'+'users_posting': ['admin',],
    'post'+'users': ['admin',],
    'put'+'users': ['admin',],
    'get'+'user_by_uuid': ['admin',],
    # user backend (auth)

    # delete items
    'delete'+'carpasses': ['admin', 'dispatcher'],
    'delete'+'exitcarpasses': ['admin', 'dispatcher'],
    'delete'+'entry_requests': ['admin', 'dispatcher', 'client', 'broker'],
    'delete'+'batches': ['admin', 'dispatcher'],
    'delete'+'dtreg': ['admin', 'dispatcher'],
    'delete'+'requests_batch_to_sklad': ['admin', 'dispatcher'],
    'delete'+'cert_goods_accept': ['admin', 'dispatcher'],
    'delete'+'contacts': ['admin', 'dispatcher'],
    'delete'+'users': ['admin',],
    'delete'+'document_records': ['admin', 'dispatcher', 'client', 'broker'],
    'delete'+'related_contact_broker': ['admin', 'dispatcher'],
    'delete'+'related_docs_record': ['admin', 'dispatcher', 'client', 'broker'],

    # rollback items
    'put'+'carpasses_rollback': ['admin', 'dispatcher',],
    'put'+'exitcarpasses_rollback': ['',],  # operation is not using
    'put'+'entry_requests_rollback': ['admin', 'dispatcher', 'client', 'broker'],
    'put'+'batches_rollback': ['admin', 'dispatcher',],
    'put'+'dtreg_rollback': ['admin', 'dispatcher',],
    'put'+'requests_batch_to_sklad_rollback': ['admin', 'dispatcher',],
    'put'+'cert_goods_accept_rollback': ['admin', 'dispatcher',],
    'put'+'contacts_rollback': ['admin', 'dispatcher',],
    'put'+'users_rollback': ['admin',],
    'put'+'document_records_rollback': ['',],  # operation is not using

    # batches
    'get'+'batches': ['admin', 'dispatcher',],
    'get'+'batches_client': ['admin','client','broker'],
    'put'+'set_batch_status': ['admin', 'dispatcher'],
    # batches card
    'get'+'related_contact_broker': ['admin', 'dispatcher', 'client', 'broker'],
    'get'+'contacts_posted': ['admin', 'dispatcher', 'client', 'broker'],
    'get'+'carpasses_posted_not_archival': ['admin', 'dispatcher', 'client', 'broker'],
    'get'+'contacts_by_uuid': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],
    'put'+'batch_posting': ['admin', 'dispatcher',],
    'post'+'batches': ['admin', 'dispatcher',],
    'put'+'batches': ['admin', 'dispatcher',],
    'get'+'batch_by_uuid': ['admin', 'dispatcher', 'client', 'broker'],
    'get'+'log_records_batch': ['admin', 'dispatcher', 'client', 'broker'],

    # carpasses
    'get'+'carpasses': ['admin', 'dispatcher'],
    'get'+'carpasses_client': ['admin','client','broker'],
    'get'+'carpasses_posted': ['admin', 'dispatcher', 'checkpoint'],
    'get'+'car_terminal': ['admin', 'dispatcher', 'checkpoint'],
    'put'+'car_exit_permit': ['admin', 'dispatcher'],
    'put'+'exit_prohibited': ['admin', 'dispatcher'],
    'put'+'set_default_car_status': ['admin', 'dispatcher'],
    # carpasses card
    'get'+'tcell_by_zone_id': ['admin', 'dispatcher',],
    'get'+'entry_requests_for_new_carpass': ['admin', 'dispatcher',],
    'get'+'tzone': ['admin', 'dispatcher',],
    'get'+'batches_by_carpass_uuid': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],
    'put'+'carpasses_posting': ['admin', 'dispatcher',],
    'post'+'carpasses': ['admin', 'dispatcher',],
    'put'+'carpasses': ['admin', 'dispatcher',],
    'get'+'carpass_by_uuid': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],

    # entry_requests
    'get'+'entry_requests': ['admin', 'dispatcher'],
    'get'+'entry_requests_client': ['admin','client','broker'],
    'get'+'entry_requests_posted': ['admin', 'dispatcher', 'checkpoint'],
    # entrty_request card
    'put'+'entry_requests_posting': ['admin', 'dispatcher', 'client', 'broker'],
    'post'+'entry_requests': ['admin', 'dispatcher', 'client', 'broker'],
    'put'+'entry_requests': ['admin', 'dispatcher', 'client', 'broker'],
    'get'+'entry_request_by_uuid': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker',],

    # exitcarpasses
    'get'+'exitcarpasses': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],
    'get'+'car_terminal_for_exit': ['admin', 'dispatcher', 'checkpoint'],
    # exitcarpasses card
    'get'+'carpass_by_id_enter': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],
    'put'+'exitcarpasses_posting': ['admin', 'dispatcher',],
    'post'+'exitcarpasses': ['admin', 'dispatcher',],
    'put'+'exitcarpasses': ['admin', 'dispatcher',],
    'get'+'exitcarpass_by_uuid': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker',],
    'put'+'car_exit': ['admin', 'checkpoint',],

    # document_records
    'get'+'document_records': ['admin', 'dispatcher',],
    'get'+'document_records_client': ['admin','client','broker'],
    # document_records card
    'get'+'entity_documents': ['admin', 'dispatcher', 'client', 'broker'],
    'get'+'related_docs': ['admin', 'dispatcher', 'client', 'broker'],
    'put'+'document_records_posting': ['',],  # operation is not using
    'post'+'document_records': ['admin', 'dispatcher', 'checkpoint', 'client', 'broker'],
    'put'+'document_records': ['admin', 'dispatcher', 'client', 'broker'],

    # contacts
    'get'+'contacts': ['admin', 'dispatcher',],
    # contacts card
    'get'+'brokers_posted': ['admin', 'dispatcher',],
    'get'+'brokers_available': ['admin', 'dispatcher',],
    'put'+'contacts_posting': ['admin', 'dispatcher',],
    'post'+'contacts': ['admin', 'dispatcher',],
    'put'+'contacts': ['admin', 'dispatcher',],
    'post'+'create_related_contact_broker': ['admin', 'dispatcher',],

    # brokers
    'get'+'brokers': ['admin', 'dispatcher',],
    # brokers card
    'get'+'related_broker_contact': ['admin', 'dispatcher',],

    # dtreg
    'get'+'dtreg': ['admin', 'dispatcher',],
    # dtreg card
    'get'+'batches_posted': ['admin', 'dispatcher',],
    'get'+'batch_by_uuid_joined': ['admin', 'dispatcher',],
    'put'+'dtreg_posting': ['admin', 'dispatcher',],
    'post'+'dtreg': ['admin', 'dispatcher',],
    'put'+'dtreg': ['admin', 'dispatcher',],
    'get'+'dtreg_by_uuid': ['admin', 'dispatcher',],

    # requests_batch_to_sklad
    'get'+'requests_batch_to_sklad': ['admin', 'dispatcher',],
    # requests_batch_to_sklad card
    'get'+'batches_for_request_goods_accept': ['admin', 'dispatcher',],
    'put'+'requests_batch_to_sklad_posting': ['admin', 'dispatcher',],
    'post'+'requests_batch_to_sklad': ['admin', 'dispatcher',],
    'put'+'requests_batch_to_sklad': ['admin', 'dispatcher',],

    # cert_goods_accept
    'get'+'cert_goods_accept': ['admin', 'dispatcher',],
    # cert_goods_accept card
    'get'+'requests_batch_to_sklad_for_cert': ['admin', 'dispatcher',],
    'get'+'requests_batch_to_sklad_by_uuid': ['admin', 'dispatcher',],
    'put'+'cert_goods_accept_posting': ['admin', 'dispatcher',],
    'post'+'cert_goods_accept': ['admin', 'dispatcher',],
    'put'+'cert_goods_accept': ['admin', 'dispatcher',],
    'get'+'cert_goods_accept_by_uuid': ['admin', 'dispatcher',],



}
