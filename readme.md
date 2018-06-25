### 基于SQLAdvisor的web界面
![](static/img/sqladvisor-web.png)

### SQLAdvisor简介
SQLAdvisor是由美团点评公司技术工程部DBA团队（北京）开发维护的一个分析SQL给出索引优化建议的工具。它基于MySQL原生态词法解析，结合分析SQL中的where条件、聚合条件、多表Join关系 给出索引优化建议。目前SQLAdvisor在美团点评内部广泛应用，公司内部对SQLAdvisor的开发全面转到github上
，开源和内部使用保持一致。

主要功能：输出SQL索引优化建议

### [SQLAdvisor](https://github.com/Meituan-Dianping/SQLAdvisor)

###环境说明
- 系统：centos6.x 64位
- python： 2.6.x 


###部署

1. 安装sqladvisor 
		
	sh scripts/installSQLAdvisor.sh

2. 安装依赖

	pip install -r requirements.txt 

3. 运行
	
	nohup python run.py &
4. 日志

	/var/log/sqladvisor.log

#####注意： 启动redis才能正常计数，否则数字处显示为N

