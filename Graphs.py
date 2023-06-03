import math
import random

import PySimpleGUI as sg
import networkx as nx
import numpy as np
from PIL import ImageGrab

import anneal
import ant


class Node:
    def __init__(self, center: (int, int), figure):
        self.center = center
        self.radius = 40
        self.figure = figure


class Line:
    def __init__(self, start, end, weight, arrow_mid):
        self.start = start
        self.end = end
        self.weight = weight
        self.arrow_mid = arrow_mid


class Graph:
    def __init__(self):
        self.nxG = nx.Graph()
        self.nodes = []
        self.lines = []
        self.pos = {}
        self.vertex_count = 0
        self.selected_vertex = None

    def weight(self, start, end):
        return ((start[0] - end[0]) ** 2 + (start[1] - end[1]) ** 2) ** 0.5

    def add_node(self, start_point, prior_rect):
        N = Node(start_point, prior_rect)
        self.nodes.append(N)
        self.nxG.add_node(N)

    def add_lines(self, startflag, endflag, prior_mid):
        L = Line(startflag, endflag, ((self.nodes[startflag].center[0] - self.nodes[endflag].center[0]) ** 2 + (
                self.nodes[startflag].center[1] - self.nodes[endflag].center[1]) ** 2) ** 0.5, prior_mid)
        self.lines.append(L)
        self.nxG.add_edge(self.nodes[startflag], self.nodes[endflag], weight=L.weight)

    def reimage(self, im, new_graph: nx.Graph):
        for edge in self.nxG.edges:
            if edge not in new_graph.edges and (edge[1], edge[0]) not in new_graph.edges:
                for i in self.lines:
                    if (edge[0] == self.nodes[i.start] and edge[1] == self.nodes[i.end]) or (
                            edge[1] == self.nodes[i.start] and edge[0] == self.nodes[i.end]):
                        print(self.nxG.edges)
                        print(self.lines)
                        im.delete_figure(i.arrow_mid)
                        self.nxG.remove_edge(edge[0], edge[1])
                        # try:
                        #  self.nxG.remove_edge(self.lines[i.start],self.lines[i.end])
                        # except:
                        #  self.nxG.remove_edge(self.lines[i.end], self.lines[i.start])
                        self.lines.pop(self.lines.index(i))
                        print(self.nxG.edges)
                        print(self.lines)

        print("full", self.nxG.edges)
        print("new", new_graph.edges)

    def complete(self, graph):
        for first in self.nxG.nodes:
            for second in self.nxG.nodes:
                if (first, second) not in self.nxG.edges and (second, first) not in self.nxG.edges:
                    self.add_lines(self.nodes.index(first), self.nodes.index(second),
                                   graph.draw_line(first.center, second.center, width=4))


def arrow(x, k, start_point, end_point):
    x1, x2 = x
    # k1 = ((end_point[1]-start_point[1])/(end_point[0]-end_point[0])+k)
    y1, y2 = (k * x1 + end_point[1] - k * end_point[0], k * x2 + end_point[1] - k * end_point[0])
    x_true = x[np.argmin([math.dist((x1, y1), start_point), math.dist((x2, y2), start_point)])]
    y_true = k * x_true + end_point[1] - k * end_point[0]
    return x_true, y_true


def save_element_as_file(element, filename):
    """
    Saves any element as an image file.  Element needs to have an underlyiong Widget available (almost if not all of
    them do) :param element: The element to save :param filename: The filename to save to. The extension of the
    filename determines the format (jpg, png, gif, ?)
    """
    widget = element.Widget
    box = (widget.winfo_rootx(), widget.winfo_rooty(), widget.winfo_rootx() + widget.winfo_width(),
           widget.winfo_rooty() + widget.winfo_height())
    grab = ImageGrab.grab(bbox=box)
    grab.save(filename)


def main():
    sg.theme('Dark Blue 3')
    col = [[sg.T('Choose what clicking a figure does', enable_events=True)],
           # [sg.R('Draw Rectangles', 1, key='-RECT-', enable_events=True)],
           [sg.R('Draw Circle', 1, key='-CIRCLE-', enable_events=True)],
           [sg.R('Draw Line', 1, key='-LINE-', enable_events=True)],
           [sg.Button('Nearest neighbours', key='-NN-')],
           [sg.Button('Annealing sim', key='-AS-')],
           [sg.Text('max t: '),
            sg.Spin(values=[i for i in range(50, 100)], initial_value=100, size=(6, 1), key='-MAXT-', readonly=True)],
           [sg.Text('min t: '),
            sg.Spin(values=[i for i in range(0, 49)], initial_value=0, size=(6, 1), key='-MINT-', readonly=True)],
           [sg.Text('step: '),
            sg.Spin(values=[i for i in range(5, 100)], initial_value=5, size=(6, 1), key='-STEP-', readonly=True)],
           [sg.Button('Ant-Q sim', key='-AN-')],
           [sg.Text('heuristic_rel: '),
            sg.Spin(values=[0.1 * i for i in range(10, 50)], initial_value=2, size=(6, 1), key='-HER-', readonly=True)],
           [sg.Text('pheromone_rel: '),
            sg.Spin(values=[0.1 * i for i in range(5, 50)], initial_value=1, size=(6, 1), key='-PHE-', readonly=True)],
           [sg.Text('ant_number: '),
            sg.Spin(values=[i for i in range(1, 500)], initial_value=50, size=(6, 1), key='-ANT-', readonly=True)],
           [sg.Text('pheromone_count: '),
            sg.Spin(values=[i for i in range(1, 50)], initial_value=10, size=(6, 1), key='-COU-', readonly=True)],
           [sg.Text('evaporation_rate: '),
            sg.Spin(values=[0.1 * i for i in range(1, 10)], initial_value=0.2, size=(6, 1), key='-EVO-',
                    readonly=True)],
           [sg.Text('iters: '),
            sg.Spin(values=[i for i in range(1, 1000)], initial_value=50, size=(6, 1), key='-ITER-',
                    readonly=True)],
           [sg.Text('gamma: '),
            sg.Spin(values=[0.1 * i for i in range(1, 10)], initial_value=0.3, size=(6, 1), key='-GAM-',
                    readonly=True)],
           [sg.Text('q0: '),
            sg.Spin(values=[0.1 * i for i in range(1, 10)], initial_value=0.9, size=(6, 1), key='-Q0-',
                    readonly=True)],
           [sg.Button('Reset options', key='-OPT-')],
           # [sg.R('Draw points', 1,  key='-POINT-', enable_events=True)],
           # [sg.R('Erase item', 1, key='-ERASE-', enable_events=True)],
           [sg.Button('Erase all', key='-CLEAR-')],
           [sg.Button('Complete graph', key='-COM-')],
           [sg.Text('Path_length: '), sg.Text('0.0', key='-CUR-')],
           # [sg.Text('Solution', key="-SOL-")]
           # [sg.R('Send to back', 1, key='-BACK-', enable_events=True)],
           # [sg.R('Bring to front', 1, key='-FRONT-', enable_events=True)],
           # [sg.R('Move Everything', 1, key='-MOVEALL-', enable_events=True)],
           # [sg.R('Move Stuff', 1, key='-MOVE-', enable_events=True)],
           # [sg.B('Save Image', key='-SAVE-')],
           ]

    layout = [[sg.Graph(
        canvas_size=(800, 800),
        graph_bottom_left=(0, 0),
        graph_top_right=(1600, 1600),
        key="-GRAPH-",
        enable_events=True,
        background_color='lightblue',
        drag_submits=True,
        right_click_menu=[[], ['Erase item', ]]
    ), sg.Col(col, key='-COL-')],
        [sg.Text(key='-INFO-', size=(60, 1))]]

    window = sg.Window("Drawing and Moving Stuff Around", layout, finalize=True)

    # get the graph element for ease of use later
    graph = window["-GRAPH-"]  # type: sg.Graph
    # graph.draw_image(data=logo200, location=(0,400))
    G = Graph()
    dragging = False
    start_point = end_point = prior_rect = prior_mid = None
    startflag = -1
    endflag = -1
    # graph.bind('<Button-3>', '+RIGHT+')

    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:
            break  # exit
        if event == "-AS-":
            graph_sol, path_len = anneal.anneal(G.nxG)
            G.reimage(graph, graph_sol)
            window['-CUR-'].update(path_len)

        if event == "-NN-":
            graph_sol, path_len = anneal.nna(G.nxG, list(G.nxG.nodes)[(random.randint(0, len(G.nxG.nodes) - 1))])
            G.reimage(graph, graph_sol)
            window['-CUR-'].update(path_len)

        if event == "-AN-":
            graph_sol, path_len = ant.aco(G.nxG)
            G.reimage(graph, graph_sol)
            window['-CUR-'].update(path_len)
        if event == "-MAXT-":
            anneal.args['max_t'] = values['-MAXT-']
        if event == "-MINT-":
            anneal.args['min_t'] = values['-MINT-']
        if event == "-MAXT-":
            anneal.args['step'] = values['-STEP-']
        if event == "-HER-":
            ant.args['heuristic_rel'] = values['-HER-']
        if event == "-PHE-":
            ant.args['pheromone_rel'] = values['-PHE-']
        if event == "-EVO-":
            ant.args['evaporation_rate'] = values['-EVO-']
        if event == "-ANT-":
            ant.args['ant_number'] = values['-ANT-']
        if event == "-COU-":
            ant.args['pheromone_count'] = values['-COU-']
        if event == "-ITER-":
            ant.args['iters'] = values['-ITER-']
        if event == "-GAM-":
            ant.args['gamma'] = values['-GAM-']
        if event == "-Q0-":
            ant.args['q0'] = values['-Q0-']
        if event == "-OPT-":
            anneal.reset_args()
            ant.reset_args()
            window["-MAXT-"].update(100)
            window["-MINT-"].update(0)
            window["-STEP-"].update(5)
            window["-Q0-"].update(0.9)
            window["-GAM-"].update(0.3)
            window["-ITER-"].update(50)
            window["-COU-"].update(10)
            window["-ANT-"].update(50)
            window["-EVO-"].update(0.2)
            window["-PHE-"].update(1)
            window["-HER-"].update(2)
        if event == "-COM-":
            G.complete(graph)
        if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
            x, y = values["-GRAPH-"]
            if not dragging:
                start_point = (x, y)
                dragging = True
                drag_figures = graph.get_figures_at_location((x, y))
                lastxy = x, y
            else:
                end_point = (x, y)
            if prior_mid:
                graph.delete_figure(prior_mid)
            # delta_x, delta_y = x - lastxy[0], y - lastxy[1]
            lastxy = x, y
            startflag = -1
            endflag = -1
            if None not in (start_point, end_point):
                # if values['-MOVE-']:
                #     for fig in drag_figures:
                #         graph.move_figure(fig, delta_x, delta_y)
                #         graph.update()
                if values['-CIRCLE-']:
                    prior_rect = graph.draw_circle(start_point, 40, fill_color='red', line_color='green')
                elif values['-LINE-']:
                    for node in G.nodes:
                        if math.dist(start_point, node.center) < 40:
                            if startflag != -1:
                                if math.dist(start_point, node) < math.dist(start_point, G.nodes[startflag]):
                                    startflag = G.nodes.index(node)
                            else:
                                startflag = G.nodes.index(node)
                        if math.dist(end_point, node.center) < 40:
                            if endflag != -1:
                                if math.dist(end_point, node.center) < math.dist(end_point, G.nodes[startflag]):
                                    endflag = G.nodes.index(node)
                            else:
                                endflag = G.nodes.index(node)
                    print(startflag, endflag)
                    prior_mid = graph.draw_line(start_point, end_point, width=4)

                # elif values['-BACK-']:
                #     for fig in drag_figures:
                #         graph.send_figure_to_back(fig)
            window["-INFO-"].update(value=f"mouse {values['-GRAPH-']}")
        elif event.endswith('+UP'):  # The drawing has ended because mouse up
            window["-INFO-"].update(value=f"grabbed rectangle from {start_point} to {end_point}")
            graph.delete_figure(prior_mid)
            if startflag != -1 and endflag != -1:
                end_point = G.nodes[endflag].center
                prior_mid = graph.draw_line(start_point, end_point, width=4)
                print(startflag, endflag, start_point, end_point)
                G.add_lines(startflag, endflag, prior_mid)
                startflag = -1
                endflag = -1
            if values['-CIRCLE-']:
                G.add_node(start_point, prior_rect)
            start_point, end_point = None, None  # enable grabbing a new rect
            dragging = False
            prior_rect = None
            prior_mid = None
        elif event.endswith('+RIGHT+'):  # Righ click
            window["-INFO-"].update(value=f"Right clicked location {values['-GRAPH-']}")
        elif event.endswith('+MOTION+'):  # Righ click
            window["-INFO-"].update(value=f"mouse freely moving {values['-GRAPH-']}")
        elif event == '-SAVE-':
            # filename = sg.popup_get_file('Choose file (PNG, JPG, GIF) to save to', save_as=True)
            filename = r'test.jpg'
            save_element_as_file(window['-GRAPH-'], filename)
        elif event == '-CLEAR-':
            graph.erase()
            G.nxG.clear()
            G.nodes = []
            G.lines = []

    window.close()


main()
