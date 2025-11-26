from src.workflows.ArxivDailyCombineWorkflow import ArxivDailyCombineWorkflow

if __name__ == '__main__':
    arxivDailyCombineWorkflow = ArxivDailyCombineWorkflow()
    with open('./publish.md','w',encoding='utf-8') as f:
        f.write(arxivDailyCombineWorkflow.combine_json_to_markdown())