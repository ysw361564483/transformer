# train 训练数据
+ question_raw.txt   
输入问题（原始形式，未作改变，原始数据已经分词，不需要额外分词）
+ parameters_raw.txt   
参数（原始形式，未作改变，暂时不需要使用）
+ question_type_raw.txt   
问题类型（原始形式，未作改变）
+ logical_form_raw.txt   
输出逻辑形式（原始形式，未作改变，已经经过基本分词）  
例如( lambda ?x ( mso:film.film.art_director "_i_see_you_"_from_avatar ?x ) )
+ logical_form_totally_tokenize.txt   
输出逻辑形式（完全分词， 在原始数据的基础上，进一步，根据所有的 : . _ 分词）  
例如( lambda ?x ( mso @:@ film @.@ film @.@ art @_@ director " @_@ i @_@ see @_@ you @_@ " @_@ from @_@ avatar ?x ) )
+ logical_form_tokenize_underline.txt   
输出逻辑形式（根据下划线分词， 在原始数据的基础上，进一步，根据所有的 _ 分词）  
例如( lambda ?x ( mso:film.film. art @_@ director " @_@ i @_@ see @_@ you @_@ " @_@ from @_@ avatar ?x ) )
+ logical_form_tokenize_just_some_underline.txt   
输出逻辑形式（根据下划线分词，在原始数据的基础上，进一步，根据部分的 _ 分词）   
例如( lambda ?x ( mso:film.film.art_director " @_@ i @_@ see @_@ you @_@ " @_@ from @_@ avatar ?x ) )
+ vocab文件夹所有词表

# dev 测试数据（完全同上）
+ question_raw.txt   
输入问题（原始形式，未作改变，原始数据已经分词，不需要额外分词）
+ parameters_raw.txt   
参数（原始形式，未作改变，暂时不需要使用）
+ question_type_raw.txt   
问题类型（原始形式，未作改变）
+ logical_form_raw.txt   
输出逻辑形式（原始形式，未作改变，已经经过基本分词）  
例如( lambda ?x ( mso:film.film.art_director "_i_see_you_"_from_avatar ?x ) )
+ logical_form_totally_tokenize.txt   
输出逻辑形式（完全分词， 在原始数据的基础上，进一步，根据所有的 : . _ 分词）  
例如( lambda ?x ( mso @:@ film @.@ film @.@ art @_@ director " @_@ i @_@ see @_@ you @_@ " @_@ from @_@ avatar ?x ) )
+ logical_form_tokenize_underline.txt   
输出逻辑形式（根据下划线分词， 在原始数据的基础上，进一步，根据所有的 _ 分词）  
例如( lambda ?x ( mso:film.film. art @_@ director " @_@ i @_@ see @_@ you @_@ " @_@ from @_@ avatar ?x ) )
+ logical_form_tokenize_just_some_underline.txt   
输出逻辑形式（根据下划线分词，在原始数据的基础上，进一步，根据部分的 _ 分词）   
例如( lambda ?x ( mso:film.film.art_director " @_@ i @_@ see @_@ you @_@ " @_@ from @_@ avatar ?x ) )
+ vocab文件夹所有词表

# 如何还原数据
还原数据代码见re_data.py
