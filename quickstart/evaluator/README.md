# Evaluator view

`hidden_ledger.csv` contains the complete synthetic query–route outcomes. The
scorer joins the selected route after validating the action file and uses the
remaining routes only to compute evaluation references and regret.

This file is evaluator input, not policy input. Its small size makes the
information boundary and arithmetic directly inspectable.
