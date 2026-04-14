import streamlit as st
import time
from collections import deque

st.set_page_config(page_title="Maze Solver", page_icon="🧩")

def valid_opt(maze, node):
    rows = len(maze)
    cols = len(maze[0])
    r, c = node

    directions = [(r-1,c), (r+1,c), (r,c-1), (r,c+1)]
    valid = []

    for nr, nc in directions:
        if 0 <= nr < rows and 0 <= nc < cols:
            if maze[nr][nc] == 0:
                valid.append((nr, nc))

    return valid

def bfs_maze(maze, start, goal, on_update=None):
    if maze[start[0]][start[1]] == 1:
        return None 

    visited = set([start])
    queue = deque([start])
    parent = {start: None}

    while queue:
        node = queue.popleft()
        
        if on_update:
            on_update(visited, node)

        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return path[::-1], len(path) - 1

        for neighbor in valid_opt(maze, node):
            if neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = node
                queue.append(neighbor)

    return None

def dfs_maze(maze, start, goal, visited=None, on_update=None):
    if maze[start[0]][start[1]] == 1:
        return None 

    if visited is None:
        visited = set()

    visited.add(start)
    if on_update:
        on_update(visited, start)

    if start == goal:
        return [start], 0

    for neighbor in valid_opt(maze, start):
        if neighbor not in visited:
            res = dfs_maze(maze, neighbor, goal, visited, on_update)
            if res:
                path, dist = res
                return [start] + path, dist + 1

    return None
    

def parse_maze(text):
    lines = text.strip().split('\n')
    maze = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ',' in line:
            parts = line.split(',')
        else:
            parts = list(line)
            
        row = []
        for p in parts:
            p = p.strip()
            if p == '0':
                row.append(0)
            elif p == '1':
                row.append(1)
                
        if row:
            maze.append(row)
            
    if not maze:
        return None, "Invalid or empty maze provided."
        
    cols = len(maze[0])
    for r in maze:
        if len(r) != cols:
            return None, "Maze is not rectangular. All rows must have the same number of columns."
            
    if len(maze) > 100 or cols > 100:
        return None, f"Maze size ({len(maze)}x{cols}) exceeds the 100x100 limit."
        
    return maze, None

def display_maze_html(maze, path, start=None, goal=None, visited=None, current=None):
    rows = len(maze)
    cols = len(maze[0])
    max_dim = max(rows, cols)
    
    # Dynamic sizing based on maze dimensions
    if max_dim <= 15:
        gap = "6px"
        font_size = "1.8rem"
        hide_text = False
        container_max_width = 450
    elif max_dim <= 40:
        gap = "2px"
        font_size = "1rem"
        hide_text = True
        container_max_width = 650
    elif max_dim <= 60:
        gap = "1px"
        font_size = "0.5rem"
        hide_text = True
        container_max_width = 800
    elif max_dim <= 80:
        gap = "1px"
        font_size = "0.35rem"
        hide_text = True
        container_max_width = 1000
    else:
        gap = "0px"
        font_size = "0.25rem"
        hide_text = True
        container_max_width = 1100
        
    html = f'''
    <style>
    @keyframes pulse-path {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 {10 if max_dim <= 40 else 2}px rgba(59, 130, 246, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }}
    }}
    .maze-container {{
        display: grid;
        grid-template-columns: repeat({cols}, minmax(0, 1fr));
        gap: {gap};
        width: min(100%, {container_max_width}px);
        max-width: 100%;
        max-height: 75vh;
        overflow: auto;
        margin: 20px auto;
        background: rgba(15, 23, 42, 0.8);
        padding: {20 if max_dim <= 40 else 5}px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }}
    .maze-cell {{
        aspect-ratio: 1 / 1;
        min-width: 0;
        min-height: 0;
        border-radius: {8 if max_dim <= 15 else (3 if max_dim <= 40 else 0)}px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: {font_size};
        transition: all 0.2s ease;
    }}
    .cell-start {{
        background: linear-gradient(135deg, #22c55e, #15803d);
        box-shadow: 0 0 {20 if max_dim <= 40 else 5}px rgba(34, 197, 94, 0.5);
        transform: scale(1.05);
        z-index: 2;
    }}
    .cell-goal {{
        background: linear-gradient(135deg, #ef4444, #b91c1c);
        box-shadow: 0 0 {20 if max_dim <= 40 else 5}px rgba(239, 68, 68, 0.5);
        transform: scale(1.05);
        z-index: 2;
    }}
    .cell-path {{
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        animation: pulse-path 2s infinite;
        z-index: 1;
        box-shadow: 0 0 {10 if max_dim <= 40 else 3}px rgba(59, 130, 246, 0.5);
    }}
    .cell-wall {{
        background: linear-gradient(135deg, #1e293b, #0f172a);
        box-shadow: inset 0 2px 5px rgba(0,0,0,0.8);
        border: 1px solid rgba(255,255,255,0.05);
    }}
    .cell-visited {{
        background: rgba(134, 239, 172, 0.6);
        box-shadow: 0 0 5px rgba(134, 239, 172, 0.3);
        border: 1px solid rgba(134, 239, 172, 0.4);
    }}
    .cell-current {{
        background: rgba(250, 204, 21, 0.9);
        transform: scale(1.1);
        z-index: 3;
        box-shadow: 0 0 10px rgba(250, 204, 21, 0.6);
    }}
    .cell-empty {{
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255,255,255,0.05);
    }}
    .cell-empty:hover {{
        background: rgba(255, 255, 255, 0.1);
        cursor: pointer;
        transform: scale(1.02);
    }}
    </style>
    <div class="maze-container">
    '''
    
    for i in range(rows):
        for j in range(cols):
            cell_class = "cell-empty"
            content = ""
            if current and (i, j) == current:
                cell_class = "cell-current"
                if not hide_text: content = "🔍"
            elif start and (i, j) == start:
                cell_class = "cell-start"
                if not hide_text: content = "🏃"
            elif goal and (i, j) == goal:
                cell_class = "cell-goal"
                if not hide_text: content = "🎯"
            elif path and (i, j) in path:
                cell_class = "cell-path"
                if not hide_text: content = "✨"
            elif visited and (i, j) in visited:
                cell_class = "cell-visited"
            elif maze[i][j] == 1:
                cell_class = "cell-wall"
                
            html += f'<div class="maze-cell {cell_class}">{content}</div>'
    
    html += "</div>"
    return html

st.title("🧩 Dynamic Maze Solver")
st.markdown("Solve any rectangular maze up to 100x100. Choose a default layout, or provide your own text/CSV!")

st.sidebar.markdown("### 📥 Maze Source")
maze_option = st.sidebar.radio("Choose Input Method", ["Default", "Text Array", "File Upload"])

parsed_maze = None
error_msg = ""
input_hash = None

if maze_option == "Default":
    parsed_maze = [
        [0,0,1,0,0],
        [1,0,1,0,1],
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,0,0,1,0],
    ]
    input_hash = "default"
elif maze_option == "Text Array":
    text_input = st.sidebar.text_area(
        "Enter maze (0 for empty, 1 for wall)", 
        "00100\n10101\n00000\n01110\n00010",
        height=200
    )
    if text_input:
        parsed_maze, error_msg = parse_maze(text_input)
        input_hash = text_input
elif maze_option == "File Upload":
    uploaded_file = st.sidebar.file_uploader("Upload .txt or .csv", type=["txt", "csv"])
    if uploaded_file is not None:
        try:
            text_input = uploaded_file.getvalue().decode("utf-8")
            parsed_maze, error_msg = parse_maze(text_input)
            input_hash = text_input
        except Exception as e:
            error_msg = f"Error reading file: {e}"

if error_msg:
    st.sidebar.error(error_msg)
    st.error("Please provide a valid maze representation.")
    st.stop()

if "input_hash" not in st.session_state or st.session_state.input_hash != input_hash:
    st.session_state.input_hash = input_hash
    if parsed_maze is not None:
        st.session_state.maze = parsed_maze

maze = st.session_state.get("maze")

if not maze:
    st.info("Waiting for maze input...")
    st.stop()

st.sidebar.markdown("### 🎛️ Configurations")

col1, col2 = st.sidebar.columns(2)
start_x = col1.number_input("Start Row", 0, len(maze)-1, 0)
start_y = col2.number_input("Start Col", 0, len(maze[0])-1, 0)

col3, col4 = st.sidebar.columns(2)
goal_x = col3.number_input("Goal Row", 0, len(maze)-1, len(maze)-1)
goal_y = col4.number_input("Goal Col", 0, len(maze[0])-1, len(maze[0])-1)

start = (start_x, start_y)
goal = (goal_x, goal_y)

algo = st.sidebar.selectbox("Choose Algorithm", ["BFS", "DFS"])

st.markdown(f"**Current Dimensions:** {len(maze)} rows × {len(maze[0])} cols")

with st.expander("🛠️ Interactive Edit Canvas (Click to toggle walls)", expanded=False):
    st.write("Click on any cell to toggle it between a Free Space (⬜) and a Wall (⬛).")
    
    rows_c = len(maze)
    cols_c = len(maze[0])
    
    if rows_c * cols_c > 400:
        st.warning("Grid is too large to elegantly render interactive clickable UI. Please modify your text layout on the sidebar instead.")
    else:
        for r in range(rows_c):
            cols_elements = st.columns(cols_c)
            for c in range(cols_c):
                cell_val = maze[r][c]
                if (r, c) == start:
                    btn_label = "🏃"
                elif (r, c) == goal:
                    btn_label = "🎯"
                else:
                    btn_label = "⬛" if cell_val == 1 else "⬜"
                    
                if cols_elements[c].button(btn_label, key=f"btn_{r}_{c}"):
                    st.session_state.maze[r][c] = 1 - st.session_state.maze[r][c]
                    st.rerun()

st.markdown("### Maze Preview & Solution")

if st.button(f"🚀 Run {algo} Animation"):
    maze_placeholder = st.empty()
    
    def on_search_update(visited, current):
        html = display_maze_html(maze, path=[], start=start, goal=goal, visited=visited, current=current)
        maze_placeholder.markdown(html, unsafe_allow_html=True)
        time.sleep(0.08)
    
    start_time = time.time()
    if algo == "BFS":
        result = bfs_maze(maze, start, goal, on_update=on_search_update)
    else:
        result = dfs_maze(maze, start, goal, visited=None, on_update=on_search_update)
    end_time = time.time()
    
    runtime_ms = (end_time - start_time) * 1000
    
    if result:
        path, steps = result
        st.success(f"**Path successfully found!** Total steps: {steps}")
        st.info(f"⏱️ **Runtime ({algo}):** {runtime_ms:.2f} ms")
        
        maze_html = display_maze_html(maze, path, start, goal, visited=None)
        maze_placeholder.markdown(maze_html, unsafe_allow_html=True)
    else:
        st.error("No path found! The current start and goal points are not connected.")
        st.info(f"⏱️ **Runtime ({algo}):** {runtime_ms:.2f} ms")
        maze_html = display_maze_html(maze, [], start, goal, visited=None)
        maze_placeholder.markdown(maze_html, unsafe_allow_html=True)
else:
    maze_placeholder = st.empty()
    maze_html = display_maze_html(maze, [], start, goal, visited=None)
    maze_placeholder.markdown(maze_html, unsafe_allow_html=True)