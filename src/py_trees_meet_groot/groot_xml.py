from xml.dom.minidom import parse, Element
import py_trees

def load(xml_file_path: str, behaviors: list = [], decorators: dict = {}):
    """Parse XML file into Song Object"""
    dict_bh = {}
    for bh in behaviors:
        dict_bh[bh.name] = bh
    
    doc = parse(xml_file_path)
    main_tree_to_execute = ""
    try:
        root = doc.getElementsByTagName("root")[0]
        print(root)
        # main_tree_to_execute = root.getAttribute("main_tree_to_execute")
        # print(main_tree_to_execute)
        behavior_trees = root.getElementsByTagName("BehaviorTree")
        for bht in behavior_trees:
            ret = parse_BehaviourTree(bht, dict_bh, decorators)
        return ret[0]
    except Exception as e :
        print(f"Exception parsing Tree: {str(e)}")
    
def parse_BehaviourTree(bh: Element, dict_bh: dict, decorators: dict) -> list:
    ret = []
    for e in bh.childNodes:
        if str(e.nodeName) == "#text":
            pass
        # Control
        elif str(e.nodeName) == "Sequence":
            nodes = parse_BehaviourTree(e, dict_bh, decorators)
            seq = py_trees.composites.Sequence(name="sequence", memory=True)
            seq.add_children(nodes)
            ret.append(seq)
        elif str(e.nodeName) == "ReactiveSequence":
            nodes = parse_BehaviourTree(e, dict_bh, decorators)
            seq = py_trees.composites.Sequence(name="sequence", memory=False)
            seq.add_children(nodes)
            ret.append(seq)
            
        elif str(e.nodeName) == "Fallback":
            nodes = parse_BehaviourTree(e, dict_bh, decorators)
            sel = py_trees.composites.Selector(name="selector", memory=True)
            sel.add_children(nodes)
            ret.append(sel)
        elif str(e.nodeName) == "ReactiveFallback":
            nodes = parse_BehaviourTree(e, dict_bh, decorators)
            sel = py_trees.composites.Selector(name="selector", memory=False)
            sel.add_children(nodes)
            ret.append(sel)
        elif str(e.nodeName) == "Parallel":
            th = None
            if e.getAttribute("success_threshold") != "":
                th = int(e.getAttribute("success_threshold"))
            if e.getAttribute("success_count") != "":
                th = int(e.getAttribute("success_count"))
            nodes = parse_BehaviourTree(e, dict_bh, decorators)
            if th == 1:
                par = py_trees.composites.Parallel(name="parallel", policy=py_trees.common.ParallelPolicy.SuccessOnOne())
            else:
                par = py_trees.composites.Parallel(name="parallel", policy=py_trees.common.ParallelPolicy.SuccessOnAll())
            par.add_children(nodes)
            ret.append(par)

        # Decorators
        elif str(e.nodeName) == "Timeout":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            print(node[0])
            dec = py_trees.decorators.Timeout(child=node[0], name="timeout", duration=float(e.getAttribute("msec"))/1000)
            ret.append(dec)
        elif str(e.nodeName) == "ForceFailure":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            print(node[0])
            dec = py_trees.decorators.SuccessIsFailure(child=node[0], name="success_is_failure")
            ret.append(dec)
        elif str(e.nodeName) == "ForceSuccess":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            print(node[0])
            dec = py_trees.decorators.FailureIsSuccess(child=node[0], name="failure_is_success")
            ret.append(dec)
        elif str(e.nodeName) == "Inverter":
            node = parse_BehaviourTree(e, dict_bh, decorators)
            print(node[0])
            dec = py_trees.decorators.Inverter(child=node[0], name="inverter")
            ret.append(dec)
        elif str(e.nodeName) == "Decorator":
            id = e.getAttribute("ID")
            print("id", id)
            print(decorators.keys())
            if id in decorators.keys():
                node = parse_BehaviourTree(e, dict_bh, decorators)
                dec = decorators[id](name=id, child=node[0])
                ret.append(dec)
            else:
                print("Unknown decorator", id)
        elif str(e.nodeName) in decorators:
            id = str(e.nodeName)
            name = id
            if e.getAttribute("name") != "":
                name = e.getAttribute("name")
            node = parse_BehaviourTree(e, dict_bh, decorators)
            dec = decorators[id](name=name, child=node[0])
            ret.append(dec)
        # Actions
        elif str(e.nodeName) == "SetBlackboard":
            output_key = e.getAttribute("output_key")
            value = e.getAttribute("value")
            set_blackboard = py_trees.behaviours.SetBlackboardVariable(
                name="set_blackboard",
                variable_name=output_key,
                variable_value=value,
                overwrite = True
            )
            ret.append(set_blackboard)
        elif str(e.nodeName) == "Action" or str(e.nodeName) == "Condition":
            if e.getAttribute("name") != "":
                name=e.getAttribute("name")
            else:
                name=e.getAttribute("ID")
            if name in dict_bh:
                ret.append(dict_bh[name])
            else:
                print("Behavior not found: ", name)
                ret.append(py_trees.behaviours.Success(name=name))
        elif str(e.nodeName) in dict_bh:
            ret.append(dict_bh[str(e.nodeName)])
        else:
            print("Unknown node " + str(e.nodeName))
    return ret    