def is_likely_real_table(table_data, min_rows=2, min_cols=2, min_cells=4):
    """
    判断是否为真实表格（而非误识别的文本）
    """
    if not table_data or len(table_data) < min_rows:
        return False
    
    # 获取最大列数（处理不规则表格）
    max_cols = max(len(row) for row in table_data if row)
    if max_cols < min_cols:
        return False

    # 总单元格数
    total_cells = sum(len(row) for row in table_data if row)
    if total_cells < min_cells:
        return False

    # 额外启发式：检查是否有“标题行”或“多列内容”
    # 比如：第一行是否明显短于其他行（可能是标题）
    # 或者是否有多列非空内容
    non_empty_cols = sum(1 for row in table_data for cell in row if cell and str(cell).strip())
    if non_empty_cols < min_cells // 2:  # 太多空单元格
        return False

    return True