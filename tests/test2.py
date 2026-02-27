import py_trees
import time
from py_trees_meet_groot import groot_xml

# Define Groot Actions and COnditions ans py_trees Behaviors

if __name__=="__main__":
    # Load Groot XML behavior tree
    root = groot_xml.load("test2.xml")
    print(py_trees.display.ascii_tree(root))
    # py_trees.display.render_dot_tree(root) # render behavior tree

    # Play Behavior Tree
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    try:
        root.setup_with_descendants()
        
        for _ in range(5):
            root.tick_once()
            time.sleep(0.5)
            print(py_trees.display.ascii_blackboard())
            print("-------------------------------------")
    except KeyboardInterrupt:
        pass