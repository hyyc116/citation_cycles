#coding:utf-8
'''
文章的作者，期刊，机构之间的关系图

'''

from basic_config import *


##首先需要获得

def get_social_attrs(pathObj):

    sccs = [line.strip().split(',') for line in open(pathObj._sccs)]

    pids = set([_id for _ids in sccs for _id in _ids ])

    logging.info('there are {:} unique papers in scc.'.format(len(pids)))

    ### 在数据库中遍历找到作者、期刊、机构
    query_op = dbop()
    sql = 'select id,title from wos_titles where title_id=1'
    pid_journal = {}
    progress = 0
    for pid,journal in query_op.query_database(sql):
        progress+=1

        if progress%10000000==0:
            logging.info('journal progress  {:} ...'.format(progress))


        if pid in pids:
            pid_journal[pid] = journal

    logging.info('{:} papers has journal info ...'.format(len(pid_journal.keys())))

    open(pathObj._journals,'w').write(json.dumps(pid_journal))
    logging.info('journal info  saved to {:}...'.format(pathObj._journals))



    sql = 'select id,full_name,seq_no from wos_summary_names where role=\'author\''

    pid_seq_author=defaultdict(dict)
    progress = 0
    for pid,author,seq_no in query_op.query_database(sql):

        progress+=1

        if progress%10000000==0:
            logging.info('author progress  {:} ...'.format(progress))

        if pid in pids:
            pid_seq_author[pid][seq_no] = author

    logging.info('{:} papers has author info ...'.format(len(pid_seq_author.keys())))

    open(pathObj._authors,'w').write(json.dumps(pid_seq_author))
    logging.info('authors info  saved to {:}...'.format(pathObj._authors))

    sql = 'select id,organization from wos_address_organizations'
    pid_orgs = defaultdict(list)
    progress = 0
    for pid,org in query_op.query_database(sql):
        progress+=1

        if progress%10000000==0:
            logging.info('org progress  {:} ...'.format(progress))

        if pid in pids:
            pid_orgs[pid].append(org)

    logging.info('{:} papers has org info ...'.format(len(pid_orgs.keys())))

    open(pathObj._orgs,'w').write(json.dumps(pid_orgs))
    logging.info('Organizations info  saved to {:}...'.format(pathObj._orgs))

    query_op.close_db()


###对于一个SCC里面，作者之间的关系
### 作者关系分为 具有相同的一作，具有相同的作者，没有相同作者， 三者之间是互斥关系
def scc_social_relations(pathObj):
    ## 加载scc
    sccs = [line.strip().split(',') for line in open(pathObj._sccs)]
    logging.info('{:} sccs are loaded ...'.format(len(sccs)))
    ##加载作者数据
    pid_seq_author= json.loads(open(pathObj._authors).read())
    logging.info('{:} paper author info are loaded.'.format(len(pid_seq_author.keys())))
    ## 加载journal的数据
    pid_journal = json.loads(open(pathObj._journals).read())
    logging.info('{:} paper journal info are loaded.'.format(len(pid_journal.keys())))
    ## 加载organization的数据
    pid_orgs = json.loads(open(pathObj._orgs).read())
    logging.info('{:} paper org info are loaded.'.format(len(pid_orgs.keys())))

    ## 加载整个图
    edges = [line.strip().split(',') for line in open(pathObj._relations)]

    ## 加载年份
    yearJson = json.loads(open(pathObj._years).read())


    dig = nx.DiGraph()
    dig.add_edges_from(edges)

    num_of_scc_used = 0
    ## 对每一个SCC进行遍历
    lines = []
    for scc in sccs:

        years = [int(yearJson[pid]) for pid in scc]
        yd = np.max(years)-np.min(years)
        size = len(scc)

        scc_edges = list(dig.subgraph(scc).edges)

        ars = []
        jrs = []
        irs = []
        for citing_pid,cited_pid in scc_edges:

            citing_seq_author = pid_seq_author.get(citing_pid,None)
            cited_seq_author = pid_seq_author.get(cited_pid,None)

            citing_journal = pid_journal.get(citing_pid,None)
            cited_journal = pid_journal.get(cited_pid,None)

            citing_insti = pid_orgs.get(citing_pid,None)
            cited_insti = pid_orgs.get(cited_pid,None)

            ar = author_relations(citing_seq_author,cited_seq_author)
            jr = journal_relations(citing_journal,cited_journal)
            ir = insti_relations(citing_insti,cited_insti)

            ars.append(ar)
            jrs.append(jr)
            irs.append(ir)

        ##有多少个scc有用
        num_of_scc_used +=1

        line = '{:}\t{:}\t{:}\t{:}\t{:}'.format(size,yd,','.join([str(a) for a in ars]),','.join([str(j) for j in jrs]),','.join([str(i) for i in irs]))
        lines.append(line)

    open(pathObj._social,'w').write('\n'.join(lines))
    logging.info('data saved to {:}.'.format(pathObj._social))


def author_relations(citing_seq_author,cited_seq_author):

    ##判断第一作者是不是相同
    if citing_seq_author is None or cited_seq_author is None:

        return -1

    elif citing_seq_author['1'] == cited_seq_author['1']:

        return 2
    ## 如果有共同作者
    elif len(set(citing_seq_author.values()) & set(cited_seq_author.values()))>0:

        return 1

    ## 如果没有共同作者
    else:
        return 0

def insti_relations(citing_insti,cited_insti):

    if citing_insti is None or cited_insti is None:
        return -1
    elif len(set(citing_insti) & set(cited_insti))>0:
        return 1
    else:
        return 0


def journal_relations(citing_journal,cited_journal):

    if citing_journal is None or cited_journal is None:
        return -1
    elif citing_journal == cited_journal:
        return 1
    else:
        return 0




## 根据生成的数据分别对三种social数据进行分析
## 如果list中存在-1那个就先舍弃
def stats_social(pathObj):

    sizes,yds,ars,jrs,irs = zip(*[line.strip().split('\t') for line in open(pathObj._social)])

    fig,axes = plt.subplots(3,2,figsize=(10,12))

    ## 对于author来讲
    all_ar_percents = []
    num_of_ars = 0
    size_ars = defaultdict(list)
    yd_ars = defaultdict(list)
    for i,ar in enumerate(ars):

        if '-1' in ar:
            continue

        num_of_ars+=1
        size = int(sizes[i])
        yd = int(yds[i])
        # all_ars.extend(ar.split(','))
        s_ars = ar.split(',')
        s_len = float(len(s_ars))
        c = Counter(s_ars)
        percent = [c.get('2',0)/s_len,c.get('1',0)/s_len,c.get('0',0)/s_len]

        size_ars[size].append(percent)
        yd_ars[yd].append(percent)
        all_ar_percents.append(percent)

    print 'all ars percentage ...'
    ar_means = percents_mean(all_ar_percents)
    print ar_means

    lines = ['|size|share 1st author|share authors|not share authors']
    lines.append('| :------: | :------: | :------: | :------: |')
    xs = []
    yses = []
    for size in sorted(size_ars.keys()):
        xs.append(size)
        ms = percents_mean(size_ars[size])
        yses.append(ms)
        line = '|{:}|{:}|'.format(size,'|'.join([str(a) for a in ms]))
        lines.append(line)
    open(pathObj._author_size_percent,'w').write('\n'.join(lines))

    ## size author
    fig_data = {}
    fig_data['x'] = xs
    fig_data['ys'] = zip(*yses)
    fig_data['title'] = 'author percent over size'
    fig_data['markers'] = [ALL_MARKERS[0],ALL_MARKERS[1],ALL_MARKERS[2]]
    fig_data['labels'] = ['share 1st author','share authors','not share author']
    fig_data['xlabel'] = 'size'
    fig_data['ylabel'] = 'percentage'
    fig_data['xscale'] = 'log'


    ax00 = axes[0,0]
    plot_multi_lines_from_data(fig_data,ax=ax00)


    lines = ['|yd|share 1st author|share authors|not share authors']
    lines.append('| :------: | :------: | :------: | :------: |')
    xs = []
    yses = []
    for yd in sorted(yd_ars.keys()):
        ms = percents_mean(yd_ars[yd])
        xs.append(yd)
        yses.append(ms)

        line = '|{:}|{:}|'.format(yd,'|'.join([str(a) for a in ms]))
        lines.append(line)
    open(pathObj._author_yd_percent,'w').write('\n'.join(lines))

    ## yd author
    fig_data = {}
    fig_data['x'] = xs
    fig_data['ys'] = zip(*yses)
    fig_data['title'] = 'author percent over year difference'
    fig_data['markers'] = [ALL_MARKERS[0],ALL_MARKERS[1],ALL_MARKERS[2]]
    fig_data['labels'] = ['share 1st author','share authors','not share author']
    fig_data['xlabel'] = 'year difference'
    fig_data['ylabel'] = 'percentage'

    ax01 = axes[0,1]
    plot_multi_lines_from_data(fig_data,ax=ax01)

    logging.info('{:} author sccs used ...'.format(num_of_ars))

    ## 对于journal来讲
    num_of_jrs = 0
    all_jrs = []
    size_jrs = defaultdict(list)
    yd_jrs = defaultdict(list)
    for i,jr in enumerate(jrs):

        if '-1' in jr:
            continue

        num_of_jrs+=1

        size = int(sizes[i])
        yd = int(yds[i])

        s_jrs = jr.split(',')
        s_len = float(len(s_jrs))
        c = Counter(s_jrs)
        percent = [c.get('1',0)/s_len,c.get('0',0)/s_len]

        all_jrs.append(percent)
        size_jrs[size].append(percent)
        yd_jrs[yd].append(percent)

    print 'journal:',percents_mean(all_jrs)
    logging.info('{:} journal scc used ...'.format(num_of_jrs))

    lines = ['|size|share 1st author|share authors|not share authors']
    lines.append('| :------: | :------: | :------: | :------: |')
    xs=[]
    yses = []
    for size in sorted(size_jrs.keys()):
        ms = percents_mean(size_jrs[size])
        xs.append(size)
        yses.append(ms)
        line = '|{:}|{:}|'.format(size,'|'.join([str(a) for a in ms]))
        lines.append(line)
    open(pathObj._journal_size_percent,'w').write('\n'.join(lines))


    ## size journal
    fig_data = {}
    fig_data['x'] = xs
    fig_data['ys'] = zip(*yses)
    fig_data['title'] = 'journal percent over size'
    fig_data['markers'] = [ALL_MARKERS[0],ALL_MARKERS[1],ALL_MARKERS[2]]
    fig_data['labels'] = ['share journal','not share journal']
    fig_data['xlabel'] = 'size'
    fig_data['ylabel'] = 'percentage'
    fig_data['xscale'] = 'log'


    ax10 = axes[1,0]
    plot_multi_lines_from_data(fig_data,ax=ax10)

    lines = ['|yd|share 1st author|share authors|not share authors']
    lines.append('| :------: | :------: | :------: | :------: |')
    xs=[]
    yses=[]
    for yd in sorted(yd_jrs.keys()):
        ms = percents_mean(yd_jrs[yd])
        xs.append(yd)
        yses.append(ms)
        line = '|{:}|{:}|'.format(yd,'|'.join([str(a) for a in ms]))
        lines.append(line)
    open(pathObj._journal_yd_percent,'w').write('\n'.join(lines))

    ## yd journal
    fig_data = {}
    fig_data['x'] = xs
    fig_data['ys'] = zip(*yses)
    fig_data['title'] = 'journal percent over year difference'
    fig_data['markers'] = [ALL_MARKERS[0],ALL_MARKERS[1]]
    fig_data['labels'] = ['share journal','not share journal']
    fig_data['xlabel'] = 'year difference'
    fig_data['ylabel'] = 'percentage'

    ax11 = axes[1,1]
    plot_multi_lines_from_data(fig_data,ax=ax11)

    ## 对于journal来讲
    num_of_irs = 0
    all_irs = []
    size_irs = defaultdict(list)
    yd_irs = defaultdict(list)
    for i,ir in enumerate(irs):

        if '-1' in ir:
            continue

        num_of_irs+=1

        size = int(sizes[i])
        yd = int(yds[i])

        s_irs = ir.split(',')
        s_len = float(len(s_irs))
        c = Counter(s_irs)
        percent = [c.get('1',0)/s_len,c.get('0',0)/s_len]

        all_irs.append(percent)
        size_irs[size].append(percent)
        yd_irs[yd].append(percent)

    print 'journal:',percents_mean(all_irs)
    logging.info('{:} organization scc used ...'.format(num_of_irs))

    lines = ['|size|share 1st author|share authors|not share authors']
    lines.append('| :------: | :------: | :------: | :------: |')
    xs=[]
    yses=[]
    for size in sorted(size_irs.keys()):
        ms = percents_mean(size_irs[size])
        xs.append(size)
        yses.append(ms)
        line = '|{:}|{:}|'.format(size,'|'.join([str(a) for a in ms]))
        lines.append(line)
    open(pathObj._insti_size_percent,'w').write('\n'.join(lines))

    ## size insti
    fig_data = {}
    fig_data['x'] = xs
    fig_data['ys'] = zip(*yses)
    fig_data['title'] = 'institute percent over size'
    fig_data['markers'] = [ALL_MARKERS[0],ALL_MARKERS[1]]
    fig_data['labels'] = ['share institute','not share institute']
    fig_data['xlabel'] = 'size'
    fig_data['ylabel'] = 'percentage'
    fig_data['xscale'] = 'log'

    ax11 = axes[2,0]
    plot_multi_lines_from_data(fig_data,ax=ax11)

    lines = ['|yd|share 1st author|share authors|not share authors']
    lines.append('| :------: | :------: | :------: | :------: |')
    xs=[]
    yses=[]
    for yd in sorted(yd_irs.keys()):
        ms = percents_mean(yd_irs[yd])
        xs.append(yd)
        yses.append(ms)
        line = '|{:}|{:}|'.format(yd,'|'.join([str(a) for a in ms]))
        lines.append(line)
    open(pathObj._insti_yd_percent,'w').write('\n'.join(lines))

    ## yd insti
    fig_data = {}
    fig_data['x'] = xs
    fig_data['ys'] = zip(*yses)
    fig_data['title'] = 'institute percent over year difference'
    fig_data['markers'] = [ALL_MARKERS[0],ALL_MARKERS[1]]
    fig_data['labels'] = ['share institute','not share institute']
    fig_data['xlabel'] = 'year difference'
    fig_data['ylabel'] = 'percentage'

    ax11 = axes[2,1]
    plot_multi_lines_from_data(fig_data,ax=ax11)

    plt.tight_layout()
    plt.savefig(pathObj._social_fig,dpi=300)
    logging.info('social fig saved to {:}.'.format(pathObj._social_fig))

def percents_mean(percents):
    # ar_counter = Counter(all_ars)
    cols = zip(*percents)

    means = []
    for col in cols:
        means.append(np.mean(col))

    return means


if __name__ == '__main__':

    data = int(sys.argv[1])

    if data==0:
        pathObj = PATHS('physics')
    else:
        pathObj = PATHS('computer science')


    # get_social_attrs(pathObj)
    # scc_social_relations(pathObj)
    stats_social(pathObj)



