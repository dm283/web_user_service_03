endpoint_allowed_roles_dict = {
    'put'+'/upload_file/': ['admin',],
    'put'+'/upload_excel_list/': ['admin',],
    'put'+'/upload_file_for_carpass/': ['ALL', ],
    'get'+'car_terminal': ['admin',],
    

    # delete items
    'delete'+'carpasses': ['admin',],
    'delete'+'exitcarpasses': ['admin',],
    'delete'+'entry_requests': ['admin','client','broker'],
    'delete'+'batches': ['admin',],
    'delete'+'dtreg': ['admin',],
    'delete'+'requests_batch_to_sklad': ['admin',],
    'delete'+'cert_goods_accept': ['admin',],
    'delete'+'contacts': ['admin',],
    'delete'+'users': ['admin',],
    'delete'+'document_records': ['admin',],
    'delete'+'related_contact_broker': ['admin',],
    'delete'+'related_docs_record': ['admin','client','broker'],

    # rollback items
    'put'+'carpasses_rollback': ['admin',],
    'put'+'exitcarpasses_rollback': ['',],  # operation is not using
    'put'+'entry_requests_rollback': ['admin','client','broker'],
    'put'+'batches_rollback': ['admin',],
    'put'+'dtreg_rollback': ['admin',],
    'put'+'requests_batch_to_sklad_rollback': ['admin',],
    'put'+'cert_goods_accept_rollback': ['admin',],
    'put'+'contacts_rollback': ['admin',],
    'put'+'users_rollback': ['admin',],
    'put'+'document_records_rollback': ['',],  # operation is not using


    # batches
    'get'+'batches': ['admin',],
    'get'+'batches_client': ['admin','client','broker'],
    # batches card
    'get'+'related_contact_broker': ['admin','client','broker'],
    'get'+'contacts_posted': ['admin','client1','broker'],
    'get'+'carpasses_posted_not_archival': ['admin','client1','broker'],
    'get'+'contacts_by_uuid': ['admin','client','broker'],
    'get'+'carpass_by_uuid': ['admin','client','broker'],
    'get'+'obj_docs': ['admin','client','broker'],
    'put'+'batch_posting': ['admin',],
    'post'+'batches': ['admin',],
    'put'+'batches': ['admin',],
    'post'+'create_related_docs_record': ['admin','client','broker',],
    'get'+'download-file': ['admin','client','broker'],
    'get'+'batch_by_uuid': ['admin','client','broker'],

    # carpasses
    'get'+'carpasses': ['admin',],
    'get'+'carpasses_client': ['admin','client','broker'],
    # carpasses card
    'get'+'tcell_by_zone_id': ['admin',],
    'get'+'entry_requests_posted': ['admin',],
    'get'+'tzone': ['admin',],
    'get'+'batches_by_carpass_uuid': ['admin','client','broker'],
    'put'+'carpasses_posting': ['admin',],
    'post'+'carpasses': ['admin',],
    'put'+'carpasses': ['admin',],

    # entry_requests
    'get'+'entry_requests': ['admin',],
    'get'+'entry_requests_client': ['admin','client','broker'],
    # entrty_request card
    'put'+'entry_requests_posting': ['admin','client','broker'],
    'post'+'entry_requests': ['admin','client','broker'],
    'put'+'entry_requests': ['admin','client','broker'],
    'get'+'entry_request_by_uuid': ['admin','client','broker',],

    # document_records
    'get'+'document_records': ['admin',],
    'get'+'document_records_client': ['admin','client','broker'],
    # document_records card
    'get'+'entity_documents': ['admin','client','broker'],
    'get'+'related_docs': ['admin','client','broker'],
    'put'+'document_records_posting': ['',],  # operation is not using
    'post'+'document_records': ['admin','client','broker'],
    'put'+'document_records': ['admin','client','broker'],

    # contacts
    'get'+'contacts': ['admin',],
    # contacts card
    'get'+'brokers_posted': ['admin',],
    'get'+'brokers_available': ['admin',],
    'put'+'contacts_posting': ['admin',],
    'post'+'contacts': ['admin',],
    'put'+'contacts': ['admin',],
    'post'+'create_related_contact_broker': ['admin',],

    # brokers
    'get'+'brokers': ['admin',],
    # brokers card
    'get'+'related_broker_contact': ['admin',],

    # users
    'get'+'users': ['admin',],
    # user card
    # user backend (auth)

    # dtreg
    'get'+'dtreg': ['admin',],
    # dtreg card
    'get'+'batches_posted': ['admin',],
    'get'+'batch_by_uuid_joined': ['admin',],
    'put'+'dtreg_posting': ['admin',],
    'post'+'dtreg': ['admin',],
    'put'+'dtreg': ['admin',],
    'get'+'dtreg_by_uuid': ['admin',],




}
