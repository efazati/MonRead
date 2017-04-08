from pymongo import MongoClient
import copy

class monread:
    """
    Simple mongo helper
     Mongoengine reader with pymongo 
    """
    #@TODO must read from config server
    MONGODB_DB = 'dbname'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    raw_collection = ''
    _list = []
    _cached_result = ''
    query = ''
    base_monread_hole = ''
    
    def __init__(self, mongoengine_queryset='', limit=6, order=(), start=0):
        self.clean()
        self.order = order
        #@TODO create instance for get instance
        self.base_monread_hole = copy.deepcopy(self) 
        if mongoengine_queryset:
            query = mongoengine_queryset._query
            self.query = query
            self.paged = '%s_%s' %(start, start+limit)
            items = self.get_raw_documents_with_query(query, self.paged)
            self.load_data(self, items, query, self.paged)

    def __getitem__(self, item):
        # for result in self._list:
        #     if self.query == result['query'] and self.paged == result['paged']:
        #         print result
        #         return result['items'][item]
        #     elif self.query == result['query']:
        #         return result['items'][item]
        return self._list[item]

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

    def get_instance(self):
        # if self.base_monread_hole:
        #     _list = []
        #     return self.base_monread_hole
        base_monread_hole = copy.deepcopy(self) 
        base_monread_hole._list = []
        return base_monread_hole

    @property
    def get_connection(self):
        if not self.collection:
            self.collection = self.raw_collection
        if type(self.collection) == str:
            self.raw_collection = self.collection
            client = MongoClient()
            db = client[self.MONGODB_DB]
            self.collection = getattr(db, self.collection)
        return self.collection

    def load_refs(self):
        if not hasattr(self, 'ref_load'):
            return False
        for ref in self.ref_load:
            try:
                lazy_ref = getattr(self, ref['name'])
            except:
                if 'multi' in ref:
                    setattr(self, ref['name'], [])
                else:
                    setattr(self, ref['name'], None)
                continue

            if not 'model' in ref:
                model = self.get_instance()
            else:
                model = ref['model']()
            db_value = lazy_ref
            if not db_value:
                # if 'multi' in ref:
                #     setattr(self, ref['name'], [])
                # else:
                #     setattr(self, ref['name'], None)

                # print 'Bad db value', ref['name'], db_value
                continue
            if 'multi' in ref:
                lazy_ref = []
                for item in db_value:
                    # print 'Fill List', model, item
                    lazy_ref.append(model.get_document_with_ref(item))
            else:
                # print 'Fill item', model, ref['name'], db_value
                lazy_ref = model.get_document_with_ref(db_value)
            setattr(self, ref['name'], lazy_ref)
        return True

    def get_raw_documents_with_query(self, query, paged='0_1'):
        self.paged = paged
        self.query = query
        paged = paged.split('_')
        start = int(paged[0])
        end = int(paged[1])
        if self.order:
            items = self.get_connection.find(self.query).sort(self.order)[start:end]
        else:
            items = self.get_connection.find(self.query)[start:end]
        return items

    def get_raw_document_with_ref(self, object_id):
        query = {'_id': object_id}
        item = self.get_raw_documents_with_query(query)
        return item

    def get_documents_with_query(self, query, paged):
        items = self.get_raw_documents_with_query(query, paged)
        # for item in items:
        #     list.append(self.load_data(self, item))
        self.load_data(self, items, query, paged)
        return self

    def get_document_with_ref(self, object_id):
        if not object_id:
            raise
        query = {'_id': object_id}
        items = self.get_raw_documents_with_query(query)
        return self.load_data(self, items, query)[0]

    @staticmethod
    def load_data(class_obj, items, query, paged='0_1'):
        # for result in class_obj._list:
        #     if query == result['query'] and paged == result['paged']:
        #         return result['items']
        #class_obj._list.append({'query':query, 'items':[], 'paged': paged, 'collection': class_obj.raw_collection})
        item_key = []
        for item in items:
            item_monread_hole = class_obj.get_instance() #type('monreadInstance', base_monread_hole.__bases__, dict(base_monread_hole.__dict__))  
            item_monread_hole.__dict__.update(**item)
            item_monread_hole._init_default_()
            item_key.append(item_monread_hole)
        class_obj._list.append({'query':query, 'items':item_key, 'paged': paged, 'collection': class_obj.raw_collection})
        class_obj._list = item_key
        return class_obj._list

    def _init_default_(self):
        if self._id:
            self.pk = self._id
            self.id = self.pk
        self.load_refs()

    def clean(self):
        self._list = []

    def __exit__(self, exc_type, exc_value, traceback):
        self.clean()