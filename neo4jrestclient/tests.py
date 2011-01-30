import client
import unittest
#client.DEBUG=1

class NodesTestCase(unittest.TestCase):

    def setUp(self):
        self.url = "http://localhost:7474/db/data/"
        self.gdb = client.GraphDatabase(self.url)

    def test_connection_cache(self):
        import client as clientCache
        clientCache.CACHE = True
        gdb = clientCache.GraphDatabase(self.url)
        clientCache.CACHE = False
        self.assertEqual(gdb.url, self.url)

    def test_connection_debug(self):
        import client as clientDebug
        clientDebug.DEBUG = True
        gdb = clientDebug.GraphDatabase(self.url)
        clientDebug.DEBUG = False
        self.assertEqual(gdb.url, self.url)

    def test_connection_cache_debug(self):
        import client as clientCacheDebug
        clientCacheDebug.CACHE = True
        clientCacheDebug.DEBUG = True
        gdb = clientCacheDebug.GraphDatabase(self.url)
        clientCacheDebug.CACHE = False
        clientCacheDebug.DEBUG = False
        self.assertEqual(gdb.url, self.url)

    def test_create_node(self):
        n = self.gdb.nodes.create()
        self.assertEqual(n.properties, {})

    def test_create_node_properties(self):
        n = self.gdb.nodes.create(name="John Doe", profession="Hacker")
        self.assertEqual(n.properties, {"name": "John Doe",
                                        "profession": "Hacker"})

    def test_create_node_empty(self):
        n = self.gdb.nodes()
        self.assertEqual(n.properties, {})

    def test_create_node_properties_dictionary(self):
        n = self.gdb.nodes(name="John Doe", profession="Hacker")
        self.assertEqual(n.properties, {"name": "John Doe",
                                        "profession": "Hacker"})

    def test_create_node_dictionary(self):
        n = self.gdb.nodes(name="John Doe", profession="Hacker")
        self.assertEqual(n["name"], "John Doe")

    def test_create_node_get(self):
        n = self.gdb.nodes(name="John Doe", profession="Hacker")
        self.assertEqual(n.get("name"), "John Doe")

    def test_create_node_get_default(self):
        n = self.gdb.nodes(name="John Doe", profession="Hacker")
        self.assertEqual(n.get("surname", "Doe"), "Doe")

    def test_get_node(self):
        n1 = self.gdb.nodes.create(name="John Doe", profession="Hacker")
        n2 = self.gdb.nodes.get(n1.id)
        self.assertEqual(n1, n2)

    def test_get_node_url(self):
        n1 = self.gdb.nodes.create(name="John Doe", profession="Hacker")
        n2 = self.gdb.nodes.get(n1.url)
        self.assertEqual(n1, n2)

    def test_get_node_dictionary(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        n2 = self.gdb.nodes[n1.id]
        self.assertEqual(n1, n2)

    def test_get_node_dictionary_with_false(self):
        n1 = self.gdb.nodes(name="John Doe", enable=False)
        n2 = self.gdb.nodes[n1.id]
        self.assertEqual(n1.properties, n2.properties)

    def test_get_node_url_dictionary(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        n2 = self.gdb.nodes[n1.url]
        self.assertEqual(n1, n2)

    def test_set_node_property_dictionary(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        n1["name"] = "Jimmy Doe"
        n2 = self.gdb.nodes[n1.id]
        self.assertEqual(n1["name"], n2["name"])

    def test_set_node_property(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        n1.set("name", "Jimmy Doe")
        n2 = self.gdb.nodes.get(n1.id)
        self.assertEqual(n1.get("name"), n2.get("name"))

    def test_set_node_properties(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        n1.properties = {"name": "Jimmy Doe"}
        n2 = self.gdb.nodes[n1.id]
        self.assertEqual(n1.properties, n2.properties)

    def test_delete_node_property_dictionary(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        del n1["name"]
        self.assertEqual(n1.get("name", None), None)

    def test_delete_node_property(self):
        n1 = self.gdb.nodes.create(name="John Doe", profession="Hacker")
        n1.delete("name")
        self.assertEqual(n1.get("name", None), None)

    def test_delete_node_properties(self):
        n1 = self.gdb.nodes(name="John Doe", profession="Hacker")
        del n1.properties
        self.assertEqual(n1.properties, {})

    def test_delete_node(self):
        n1 = self.gdb.nodes.create(name="John Doe", profession="Hacker")
        identifier = n1.id
        n1.delete()
        try:
            self.gdb.nodes.get(identifier)
            self.fail()
        except client.NotFoundError, client.StatusException:
            pass
            self.assertTrue(True)

    def test_create_index_on_node(self):
        n1 = self.gdb.nodes.create(name='John Doe', profession='Hacker')
        n1.index(key='name', value='John Doe', create=True)
        indexed = self.gdb.index(key='name', value='John Doe')
        self.assertTrue(n1.id in indexed)

    def test_create_index_on_collection(self):
        n1 = self.gdb.nodes.create(name='John Doe', profession='Hacker')
        self.gdb.index(key='profession', value='Hacker', create=True)
        indexed = self.gdb.index(key='profession', value='Hacker')
        print indexed
        self.assertTrue(n1.id in indexed)

    def test_query_index_on_node(self):
        n1 = self.gdb.nodes.create(name='John Doe', profession='Hacker')
        n1.index(key='name', value='John Doe', create=True)
        indexed = n1.index(key='name', value='John Doe')
        self.assertTrue(len(indexed) > 0)

    def test_query_index_on_collection(self):
        n1 = self.gdb.nodes.create(name='John Doe', profession='Hacker')
        self.gdb.index(key='name', value='John Doe', create=True)
        indexed = self.gdb.index(key='name', value='John Doe')
        print indexed, n1.id
        self.assertTrue(len(indexed) > 0)

    def test_delete_index_against_collection(self):
        found = False
        n1 = self.gdb.nodes.create(name='John Doe', profession='Hacker')
        self.gdb.index(key='name', value='John Doe', create=True)
        self.gdb.index(key='name', value='John Doe', delete=True)
        indexed = self.gdb.index(key='name', value='John Doe')

        for node in indexed:
            node_it = indexed[node]
            if node_it.url == n1.url:
                found = True

        self.assertTrue(found == False)

    def test_delete_index_against_node(self):
        n1 = self.gdb.nodes.create(name='John Doe', profession='Hacker')
        self.gdb.index(key='name', value='John Doe', create=True)
        indexed = n1.index(key='name', value='John Doe', delete=True)
        self.assertTrue(len(indexed) == 0)

class RelationshipsTestCase(NodesTestCase):

    def test_create_relationship(self):
        n1 = self.gdb.nodes()
        n2 = self.gdb.nodes()
        rel = n1.Knows(n2)
        self.assertEqual(rel.properties, {})

    def test_create_relationship_functional(self):
        n1 = self.gdb.nodes.create()
        n2 = self.gdb.nodes.create()
        rel = n1.relationships.create("Knows", n2)
        self.assertEqual(rel.properties, {})

    def test_create_relationship_properties(self):
        n1 = self.gdb.nodes()
        n2 = self.gdb.nodes()
        rel = n1.Knows(n2, since=1970)
        self.assertEqual(rel.properties, {"since": 1970})

    def test_create_relationship_functional_properties(self):
        n1 = self.gdb.nodes.create()
        n2 = self.gdb.nodes.create()
        rel = n1.relationships.create("Knows", n2, since=1970)
        self.assertEqual(rel.properties, {"since": 1970})


class TraversalsTestCase(RelationshipsTestCase):

    def test_create_traversal(self):
        n1 = self.gdb.nodes.create()
        n2 = self.gdb.nodes.create()
        n1.relationships.create("Knows", n2, since=1970)
        types = [
            client.Undirected.Knows,
        ]
        traversal = n1.traverse(types=types)
        self.failUnless(len(traversal) > 0)

    def test_create_traversal_class(self):
        n1 = self.gdb.nodes.create()
        n2 = self.gdb.nodes.create()
        n1.relationships.create("Knows", n2, since=1970)

        class TraversalClass(self.gdb.Traversal):

            types = [
                client.Undirected.Knows,
            ]

        results = []
        for result in TraversalClass(n1):
            results.append(result)
        self.failUnless(len(results) > 0)


class Neo4jPythonClientTestCase(TraversalsTestCase):
    pass

if __name__ == '__main__':
    test_loader = unittest.TestLoader()
    suite = test_loader.loadTestsFromTestCase(Neo4jPythonClientTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
