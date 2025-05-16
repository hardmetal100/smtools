import networkx as nx
from PIL import Image
import numpy as np
from ete3 import Tree

from libLogging import libLogging as log

class libNetwork:
    g=None
    t=None
    config = None
    tree = None
    tree_nodes_list = None
    var = None

    @classmethod
    def __init__(cls):
        """Initialise Networkx object in form of DiGraph."""
        cls.clear()

    @classmethod
    def clear(cls):
        """Clear graph."""
        cls.g = nx.DiGraph()

    @classmethod
    def add_edge(cls, node_before, node_after):
        """
        Add edge (arrow) going from node_before to node_after.
        :param node_before: Edge startpoint
        :param node_after: Edge endpoint
        :return: None
        """
        #print ("'" + node_before + "' -> '" + node_after + "'")
        cls.g.add_edge(node_before, node_after)
        #print (list(nx.topological_sort(cls.g)))
        return None

    @classmethod
    def build_network(cls, config, seperator):
        """
        Build a network graph from a ConfigParser configuration.
        :param config: ConfigParser object
        :param seperator: A string representing the separator used to split the after/before item
        :return: None
        """
        cls.g.add_nodes_from(config.sections())
        for section in config.sections():
            for key in config[section].keys():
                if (key == "after"):
                    valuelist = config.get(section, "after")
                    for value in valuelist.split(seperator):
                        if(value != ""):
                            cls.add_edge(value.strip(), section.strip())
                elif(key =="before"):
                    valuelist = config.get(section, "before")
                    for value in valuelist.split(seperator):
                        if (value != ""):
                            cls.add_edge(section.strip(), value.strip())
        return None

    @classmethod
    def get_starting_nodes(cls):
        return [n[0] for n in cls.g.in_degree() if n[1] == 0]

    @classmethod
    def get_ending_nodes(cls):
        return [n[0] for n in cls.g.out_degree() if n[1] == 0]

    @classmethod
    def reduce(cls, root, graph):
        """
        Reduce a graph to the necessary paths for a specific root node
        :param root: Node which is the root for all paths to end nodes
        :param graph: Graph to be processed
        :return: New reduced graph
        """
        g = graph.copy()
        good_nodes = set()
        for p in cls.get_starting_nodes():
            for sp in nx.all_simple_paths(cls.g, p, root):
                [good_nodes.add(n) for n in sp]
        log.libinfo.info("Reduce to paths for root node '" + root + "'")
        to_be_removed = [n for n in g.nodes() if n not in good_nodes]
        log.libinfo.info("  remove: " + ", ".join(to_be_removed))
        g.remove_nodes_from(to_be_removed)
        return g


    @classmethod
    def levelinfo(cls, start, start_is_root=True, level=0):
        """
        This method generates a dictionary with the node name as key and the level as value.
        :param start: Start node name
        :param start_is_root: Flags start node is also the root of the path
        :param level: Actual level, shall be 0 for the first time
        :return: A dictionary {NODE-NAME: LEVEL, ...}
        """
        if start_is_root:
            cls.var = dict()

        if start not in cls.var.keys() or cls.var[start] < level:
            cls.var[start] = level

        neighbors = [n for n in cls.g.predecessors(start)]

        for n in neighbors:
            cls.levelinfo(n, start_is_root=False, level =level + 1)

        #if start_is_root:
        #    print(cls.var)
        return cls.var

    @classmethod
    def levelinfo_to_nodelist_simple(cls, levelinfo):
        """
        Convert a levelinfo dictionary {NODE-NAME: LEVEL, ...} to a NODE-NAME list in the order of the LEVELs given
        :param levelinfo: Dictionary {NODE-NAME: LEVEL, ...}
        :return: [NODE-NAME, ...] in the order of LEVEL given in dict (0, 1, 2, ...)
        """
        return [k for k, v in sorted(levelinfo.items(), key=lambda kv: kv[1])]

    @classmethod
    def levelinfo_to_nodelist(cls, levelinfo):
        nodelist = list()
        for k, v in sorted(levelinfo.items(), key=lambda kv: kv[1]):
            if len(nodelist) == v:
                nodelist.append([k])
            else:
                nodelist[v].append(k)
        return nodelist

    @classmethod
    def print_nodelist(cls, nodelist):
        log.libinfo.info('List of nodes in the selected path:')
        for i, n in enumerate(nodelist):
            if type(n) == list:
                s = ', '.join(n)
            else:
                s = n
            log.libinfo.info('  %3d. %s' % (i + 1, s))
        return None

    @classmethod
    def display_network_png(cls, root=None):
        """Create and open representation of network in form of .png."""
        cls.g.remove_edges_from(cls.g.selfloop_edges())

        if root is not None:
            cls.g = cls.reduce(root, cls.g)
        #levels = cls.levelinfo('incisive/simulation/posttasks')
        #cls.print_nodelist(cls.levelinfo_to_nodelist_simple(levels))
        #print('-' * 10)
        #cls.print_nodelist(cls.levelinfo_to_nodelist(levels))
        #print('-' * 10)

        #cls.g = cls.g.reverse()
        #cls.g = nx.dfs_tree(cls.g)
        #cls.g = nx.bfs_tree(cls.g, 'incisive/simulation/posttasks', reverse=False)
        #cls.ete3_build_tree('incisive/simulation/posttasks')
        #cls.ete3_display_asciitree()


        DOT = nx.nx_pydot.to_pydot(cls.g)
        DOT.write_png("test.png")

        f, SC, GCF, WCF = "test.png", 0.2, 10.0, 7 / 4

        img = Image.open(f)
        img.show()
        return


    @classmethod
    def ete3_add_nxnodes_to_tree(cls, start, nodes, start_is_root=False):
        i = 0
        if start_is_root:
            print (i++)
            if start is None:
                start = 'root'
            print (i++)
            cls.t = Tree("[%s];" % (start), format=1)
            print (i++)
            node = cls.t.search_nodes(name="[%s]"%(start))[0]
            print (i++)
            cls.tree_nodes_list = [start]
            print (i++)
        else:
            node = cls.t.search_nodes(name="->[%s]"%(start))[0]

        print (i++)
        for n in nodes:
            print (i++)
            if n not in cls.tree_nodes_list:
                print (i++)
                node.add_child(name="->[%s]"%(n))
                print (i++)
                cls.tree_nodes_list.append(n)
                print (i++)
        return

    @classmethod
    def ete3_build_tree(cls, start, start_is_root=True):
        """Display network using ETE3 module."""
        neighbors = [n for n in cls.g.predecessors(start)]

        cls.ete3_add_nxnodes_to_tree(start, neighbors, start_is_root)

        for n in neighbors:
            cls.ete3_build_tree(n, start_is_root=False)
        return

    @classmethod
    def ete3_display_asciitree(cls):
        """Display network using ETE3 module."""
        log.libinfo.info('Network Structure')
        if cls.t is not None:
            log.libinfo.info(cls.t.get_ascii(show_internal=True, compact=False))
        else:
            log.libinfo.info('  ** NO ELEMENTS FOUND **')
        return
