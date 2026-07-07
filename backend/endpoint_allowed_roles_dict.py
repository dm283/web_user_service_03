endpoint_allowed_roles_dict = {
    'put'+'/upload_file/': ['admin',],
    'put'+'/upload_excel_list/': ['admin',],
    'post'+'/document_records/': ['ALL', ],
    'put'+'/upload_file_for_carpass/': ['ALL', ],
    'get'+'/users/': ['admin',],

    # batches
    'get'+'batches': ['admin',],
    'get'+'batches_client': ['admin','client','broker'],
    'delete'+'batches': ['admin',],
    'put'+'batches_rollback': ['admin',],
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

}
