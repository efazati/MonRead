#MonRead
In some case Mongoengine is too slow, you can pass your mongo queryset to monread and use like some pymongo project
very fast resut can be satisfied you

# Example
```
from project.utils.MonRead import MonRead

class LightProduct(Moon):
    collection = 'product'
    
    ref_load = [
        {
        	'name':'images',
        	'model': LightGallery,
        	'multi': True
        },
        {
        	'name':'store',
        	'model': LightStore,
        },
        {
        	'name':'first_related',
        },
        {
        	'name':'products_bundled',
        	'multi': True
        },
    ]
    

    @property
    def likes_count(self):
        return len(self.likes)
    
    # mongoengine model
    product_list = \
        Product.objects(store=self, is_deleted=False,
                        first_related__exists=False,
                        published=True)
    order = [('sells_success', 1), ('likes', -1), ('visit', 1)]
    product_list = LightProduct(product_list, length, order)
    for item in product_list:
    	print item.pk

```