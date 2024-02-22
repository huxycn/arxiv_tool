import re


class PatternRecognizer:
    def __init__(self, regular_rule):
        self.pattern = re.compile(regular_rule)

    def match(self, string):
        return self.pattern.match(string)
    
    def findall(self, string):
        return self.pattern.findall(string)

    def multiple_replace(self, content, **replace_dict):
        def replace_(value):
            match = value.group()
            if match in replace_dict.keys():
                return replace_dict[match]
            else:
                return match+" **Not Correct, Check it**"
        
        replace_content = self.pattern.sub(replace_, content)
        
        return replace_content


if __name__ == '__main__':
    pattern_recognizer = PatternRecognizer(r'https://arxiv.org/abs/\d{4}.\d{5}')

    with open('../../projects/my_reading_papers/mds/Downstream-Tasks.md', 'r') as f:
        content = f.read()

    urls = pattern_recognizer.findall(content)

    replace_dict = {}

    for i, url in enumerate(urls):
        replace_dict[url] = f'{i}: {url}'
    
    replace_content = pattern_recognizer.multiple_replace(content, **replace_dict)

    print(replace_content)
