Split sources for ovning5.tex (same content as the single-file version).

Build:   pdflatex main.tex   (twice)
Regenerate the TikZ in gen/ after changing an example:
         python3 gen_mst.py; python3 gen_flow.py; python3 gen_euler.py
         python3 gen_match.py; python3 gen_lower.py; python3 gen_lamps.py
Each generator asserts the worked example before writing anything
(MST weight, flow values, Euler trace, the unique perfect matching,
insertion-sort counts for n <= 7, lamp costs for all inputs with n <= 8).
