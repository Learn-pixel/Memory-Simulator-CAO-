# memory_hierarchy_full_simulator.py
import tkinter as tk
from tkinter import ttk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------------------
# Memory Simulator (probabilistic model)
# ------------------------------
class MemorySimulator:
    def __init__(self,
                 cache_cycles=1,
                 main_cycles=10,
                 virt_cycles=1000,
                 cache_hit_rate=70.0,
                 page_present_rate=90.0):
        """
        cache_hit_rate: percentage [0..100] probability that an access hits cache
        page_present_rate: percentage [0..100] probability that a cache miss is served by main memory
                           (otherwise it's considered a page-fault -> virtual memory)
        cycles are positive integers for each memory type.
        """
        self.cache_cycle = cache_cycles
        self.main_cycle = main_cycles
        self.virt_cycle = virt_cycles

        # probabilities
        self.cache_hit_rate = cache_hit_rate
        self.page_present_rate = page_present_rate

        # Stats
        self.reset_stats()

    def reset_stats(self):
        self.accesses = 0
        self.hits = 0
        self.misses = 0
        self.page_faults = 0
        self.total_cycles = 0
        # For plotting AMAT history if desired
        self.amat_history = []

    def set_cycles(self, cache=None, main=None, virt=None):
        if cache is not None:
            self.cache_cycle = max(1, int(cache))
        if main is not None:
            self.main_cycle = max(1, int(main))
        if virt is not None:
            self.virt_cycle = max(1, int(virt))

    def set_probabilities(self, cache_hit=None, page_present=None):
        if cache_hit is not None:
            self.cache_hit_rate = max(0.0, min(100.0, float(cache_hit)))
        if page_present is not None:
            self.page_present_rate = max(0.0, min(100.0, float(page_present)))

    def access_once(self, forced_outcome=None):
        """
        Simulate a single memory access.
        forced_outcome: None, 'cache', 'main', or 'virt' to force which level is used.
        Returns: (used_level, cycles)
        used_level is one of 'cache', 'main', 'virt'
        """
        self.accesses += 1

        if forced_outcome is not None:
            outcome = forced_outcome
        else:
            rnd = random.uniform(0, 100)
            if rnd <= self.cache_hit_rate:
                outcome = 'cache'
            else:
                # cache miss -> check if in main memory or page-fault
                rnd2 = random.uniform(0, 100)
                if rnd2 <= self.page_present_rate:
                    outcome = 'main'
                else:
                    outcome = 'virt'

        if outcome == 'cache':
            self.hits += 1
            cycles = self.cache_cycle
        elif outcome == 'main':
            self.misses += 1
            cycles = self.main_cycle
        else:  # virt
            self.misses += 1
            self.page_faults += 1
            cycles = self.virt_cycle

        self.total_cycles += cycles
        amat = (self.total_cycles / self.accesses) if self.accesses > 0 else 0.0
        self.amat_history.append(amat)
        return outcome, cycles, amat

    def get_stats(self):
        if self.accesses == 0:
            return {
                'accesses': 0, 'hits': 0, 'misses': 0, 'page_faults': 0,
                'hit_ratio': 0.0, 'page_fault_rate': 0.0, 'amat': 0.0
            }
        hit_ratio = (self.hits / self.accesses) * 100.0
        page_fault_rate = (self.page_faults / self.accesses) * 100.0
        amat = self.total_cycles / self.accesses
        return {
            'accesses': self.accesses,
            'hits': self.hits,
            'misses': self.misses,
            'page_faults': self.page_faults,
            'hit_ratio': hit_ratio,
            'page_fault_rate': page_fault_rate,
            'amat': amat
        }

# ------------------------------
# GUI Application
# ------------------------------
class MemoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Memory Hierarchy Visual Simulator — Full Version")
        self.root.geometry("1050x720")
        # default simulator
        self.sim = MemorySimulator()

        self._build_gui()
        self._init_plot()

    def _build_gui(self):
        # Top title
        title = tk.Label(self.root, text="Memory Hierarchy Visual Simulator (Cache / Main / Virtual)",
                         font=("Segoe UI", 16, "bold"))
        title.pack(pady=8)

        # Controls frame
        controls = ttk.Frame(self.root)
        controls.pack(fill='x', padx=10)

        # Left: sliders for cycles and probabilities
        left = ttk.LabelFrame(controls, text="Timing & Probability Controls", padding=8)
        left.grid(row=0, column=0, padx=8, pady=4, sticky='nw')

        # Cache access time slider
        ttk.Label(left, text="Cache access time (cycles)").grid(row=0, column=0, sticky='w')
        self.cache_cycle_var = tk.IntVar(value=self.sim.cache_cycle)
        self.cache_scale = tk.Scale(left, from_=1, to=50, orient='horizontal', variable=self.cache_cycle_var,
                                    command=self._on_slider_change, length=260)
        self.cache_scale.grid(row=1, column=0, padx=4, pady=2)

        # Main memory access time
        ttk.Label(left, text="Main memory access time (cycles)").grid(row=2, column=0, sticky='w')
        self.main_cycle_var = tk.IntVar(value=self.sim.main_cycle)
        self.main_scale = tk.Scale(left, from_=2, to=200, orient='horizontal', variable=self.main_cycle_var,
                                   command=self._on_slider_change, length=260)
        self.main_scale.grid(row=3, column=0, padx=4, pady=2)

        # Virtual memory access time
        ttk.Label(left, text="Virtual memory access time (cycles)").grid(row=4, column=0, sticky='w')
        self.virt_cycle_var = tk.IntVar(value=self.sim.virt_cycle)
        self.virt_scale = tk.Scale(left, from_=50, to=20000, orient='horizontal', variable=self.virt_cycle_var,
                                   command=self._on_slider_change, length=260, resolution=50)
        self.virt_scale.grid(row=5, column=0, padx=4, pady=2)

        # Cache hit rate slider
        ttk.Label(left, text="Cache hit rate (%)").grid(row=6, column=0, sticky='w')
        self.cache_hit_var = tk.DoubleVar(value=self.sim.cache_hit_rate)
        self.cache_hit_scale = tk.Scale(left, from_=0, to=100, orient='horizontal', variable=self.cache_hit_var,
                                        command=self._on_slider_change, length=260, resolution=1.0)
        self.cache_hit_scale.grid(row=7, column=0, padx=4, pady=2)

        # Page present rate slider
        ttk.Label(left, text="Page present in RAM on cache-miss (%)").grid(row=8, column=0, sticky='w')
        self.page_present_var = tk.DoubleVar(value=self.sim.page_present_rate)
        self.page_present_scale = tk.Scale(left, from_=0, to=100, orient='horizontal', variable=self.page_present_var,
                                           command=self._on_slider_change, length=260, resolution=1.0)
        self.page_present_scale.grid(row=9, column=0, padx=4, pady=2)

        # Right: action buttons and stats
        right = ttk.LabelFrame(controls, text="Actions & Stats", padding=8)
        right.grid(row=0, column=1, padx=8, pady=4, sticky='ne')

        # Manual address entry (conceptual - we use probabilistic outcomes)
        ttk.Label(right, text="(Simulation uses probabilities; addresses are conceptual)").grid(row=0, column=0, columnspan=3, pady=2)
        ttk.Label(right, text="Number of random accesses:").grid(row=1, column=0, sticky='w')
        self.num_access_entry = ttk.Entry(right, width=8)
        self.num_access_entry.insert(0, "10")
        self.num_access_entry.grid(row=1, column=1, sticky='w', padx=4)
        ttk.Button(right, text="Run N Random", command=self.run_n_random).grid(row=1, column=2, padx=6)

        ttk.Separator(right, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=6)

        ttk.Button(right, text="Access Once", command=self.access_once).grid(row=3, column=0, padx=6, pady=2)
        ttk.Button(right, text="Random Access", command=self.random_access).grid(row=3, column=1, padx=6, pady=2)
        ttk.Button(right, text="Reset Stats", command=self.reset_stats).grid(row=3, column=2, padx=6, pady=2)

        # Stats text area
        self.stats_text = tk.Text(right, width=36, height=12, wrap='word')
        self.stats_text.grid(row=4, column=0, columnspan=3, pady=6)
        self.stats_text.configure(state='disabled')

        # Bottom: plot area
        plot_frame = ttk.Frame(self.root)
        plot_frame.pack(fill='both', expand=True, padx=10, pady=6)

        self.fig, self.ax = plt.subplots(figsize=(8,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        # Info / legend below plot
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill='x', padx=10, pady=4)
        self.last_access_label = ttk.Label(info_frame, text="Last Access: -")
        self.last_access_label.pack(side='left', padx=6)
        self.amat_label = ttk.Label(info_frame, text="AMAT: -")
        self.amat_label.pack(side='left', padx=30)

        # initialize display
        self._update_stats_display()

    def _init_plot(self):
        # Initial static plot showing baseline cycle values
        self.ax.clear()
        types = ['Cache', 'Main Memory', 'Virtual Memory']
        cycles = [self.sim.cache_cycle, self.sim.main_cycle, self.sim.virt_cycle]
        colors = ['#2ca02c', '#ff7f0e', '#d62728']  # green, orange, red
        bars = self.ax.bar(types, cycles, color=colors)
        self.ax.set_title('Access Time per Level (cycles) — Last Access Highlighted')
        self.ax.set_ylabel('Cycles')
        self.ax.grid(axis='y', linestyle='--', alpha=0.6)

        # put numbers above bars
        for bar in bars:
            y = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2, y + y*0.02 + 5, f"{int(y)}", ha='center', va='bottom', fontsize=10)

        self.canvas.draw()

    def _on_slider_change(self, _=None):
        # update simulator parameters live as sliders move
        self.sim.set_cycles(cache=self.cache_cycle_var.get(),
                            main=self.main_cycle_var.get(),
                            virt=self.virt_cycle_var.get())
        self.sim.set_probabilities(cache_hit=self.cache_hit_var.get(),
                                   page_present=self.page_present_var.get())
        # update initial / baseline plot (no highlight)
        self._init_plot()
        self._update_stats_display()

    def access_once(self):
        outcome, cycles, amat = self.sim.access_once()
        self._display_access_result(outcome, cycles, amat)

    def random_access(self):
        outcome, cycles, amat = self.sim.access_once()
        self._display_access_result(outcome, cycles, amat)

    def run_n_random(self):
        try:
            n = int(self.num_access_entry.get())
            if n <= 0:
                return
        except ValueError:
            return
        # run n accesses quickly and update final state & plot animation for each (fast)
        for _ in range(n):
            outcome, cycles, amat = self.sim.access_once()
        # display the last result
        self._display_access_result(outcome, cycles, amat)

    def reset_stats(self):
        self.sim.reset_stats()
        self._init_plot()
        self._update_stats_display()
        self.last_access_label.config(text="Last Access: -")
        self.amat_label.config(text=f"AMAT: 0.00 cycles")

    def _display_access_result(self, outcome, cycles, amat):
        # Update last access label
        self.last_access_label.config(text=f"Last Access: {outcome.upper()} (cycles = {cycles})")
        self.amat_label.config(text=f"AMAT: {amat:.2f} cycles")
        # update stats text
        self._update_stats_display()
        # update dynamic plot to highlight which level was used for this access
        self._update_dynamic_plot(outcome, cycles)

    def _update_stats_display(self):
        stats = self.sim.get_stats()
        s = (
            f"Total Accesses: {stats['accesses']}\n"
            f"Cache Hits: {stats['hits']}\n"
            f"Cache Misses: {stats['misses']}\n"
            f"Page Faults: {stats['page_faults']}\n\n"
            f"Cache Hit Ratio: {stats['hit_ratio']:.2f} %\n"
            f"Page Fault Rate: {stats['page_fault_rate']:.2f} %\n\n"
            f"Average Memory Access Time (AMAT): {stats['amat']:.2f} cycles\n\n"
            f"Current Settings:\n"
            f" - Cache time = {self.sim.cache_cycle} cycles\n"
            f" - Main memory time = {self.sim.main_cycle} cycles\n"
            f" - Virtual memory time = {self.sim.virt_cycle} cycles\n"
            f" - Cache hit rate = {self.sim.cache_hit_rate:.1f} %\n"
            f" - Page present rate = {self.sim.page_present_rate:.1f} %"
        )
        self.stats_text.configure(state='normal')
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert(tk.END, s)
        self.stats_text.configure(state='disabled')

    def _update_dynamic_plot(self, outcome, cycles):
        # Prepare bars showing last-access emphasis:
        self.ax.clear()
        types = ['Cache', 'Main Memory', 'Virtual Memory']
        # We will set only the used level to its cycles; others to small baseline (0 or 0.1)
        baseline = 0.0
        cycles_list = [
            cycles if outcome == 'cache' else baseline,
            cycles if outcome == 'main' else baseline,
            cycles if outcome == 'virt' else baseline
        ]
        # Use colors where only the used bar is bright
        colors = []
        for t in types:
            if (t == 'Cache' and outcome == 'cache'):
                colors.append('#2ca02c')  # green
            elif (t == 'Main Memory' and outcome == 'main'):
                colors.append('#ff7f0e')  # orange
            elif (t == 'Virtual Memory' and outcome == 'virt'):
                colors.append('#d62728')  # red
            else:
                colors.append('#bdbdbd')  # grey for inactive

        bars = self.ax.bar(types, cycles_list, color=colors)
        self.ax.set_title('Access Time per Level (last access highlighted)')
        self.ax.set_ylabel('Cycles')
        self.ax.grid(axis='y', linestyle='--', alpha=0.6)

        # place numerical labels on top of each bar
        for bar_index, bar in enumerate(bars):
            yval = bar.get_height()
            # place label slightly above bar; if baseline is 0, show 0
            label = f"{int(yval)}" if yval >= 1 else "0"
            self.ax.text(bar.get_x() + bar.get_width()/2, yval + max(1.0, yval*0.02) + 3,
                         label, ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Also draw a small horizontal line representing AMAT for context
        stats = self.sim.get_stats()
        amat = stats['amat']
        if amat > 0:
            # limit amat line to reasonable y-range
            ymax = max(max(cycles_list), amat) * 1.2 if max(cycles_list) > 0 else amat * 1.2
            self.ax.set_ylim(0, max(50, ymax))
            self.ax.axhline(amat, color='blue', linestyle=':', linewidth=1.5)
            self.ax.text(2.85, amat + max(1.0, amat*0.02), f"AMAT={amat:.2f}c", color='blue', fontsize=9, ha='right')

        self.canvas.draw()

# ------------------------------
# Run the App
# ------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = MemoryApp(root)
    root.mainloop()
