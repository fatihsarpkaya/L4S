all: single_bottleneck.ipynb

clean:
	rm single_bottleneck.ipynb

SNIPPETS := fabric-snippets/fab-config.md fabric-snippets/reserve-resources.md fabric-snippets/extend.md fabric-snippets/configure-resources.md fabric-snippets/offload-off.md custom-snippets/exp-configure.md fabric-snippets/draw-topo-detailed-labels.md fabric-snippets/log-in.md custom-snippets/exp-define.md custom-snippets/exp-execute.md custom-snippets/exp-analyze.md
single_bottleneck.ipynb: $(SNIPPETS)
	pandoc --wrap=none \
                fabric-snippets/fab-config.md \
                custom-snippets/exp-define.md \
                fabric-snippets/reserve-resources.md \
		fabric-snippets/extend.md \
                custom-snippets/exp-configure.md \
                fabric-snippets/configure-resources.md \
                fabric-snippets/offload-off.md \
                fabric-snippets/draw-topo-detailed-labels.md \
		fabric-snippets/log-in.md \
                custom-snippets/exp-execute.md \
                custom-snippets/exp-analyze.md \
                -o single_bottleneck.ipynb  
