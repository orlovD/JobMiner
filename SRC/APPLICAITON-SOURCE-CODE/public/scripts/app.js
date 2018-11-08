var Page = React.createClass({
	getInitialState: function(){
		return {data:[]};
	},
	loadPostsFromServer: function(){
		$.ajax({
			url: this.props.url,
			dataType: 'json',
			cache: false,
			success: function(data){
				this.setState({data: data});
			}.bind(this),
			error: function(xhr, status, err) {
				console.error(this.props.url, status, err.toString());
			}.bind(this)
		});
	},
	onSubmitSearchQuery: function(query, callback){
		console.log('query');
		console.log(JSON.stringify(query));
		$.ajax({
		    type: "POST",
		    url: this.props.url,
		    // The key needs to match your method's input parameter (case-sensitive).
		    data: JSON.stringify(query),
		    contentType: "application/json; charset=utf-8",
		    dataType: "json",
			success: function(data){
				console.log('success');
				this.setState({data: data});
				callback();
			}.bind(this),
			error: function(xhr, status, err) {
				console.error(this.props.url, status, err.toString());
				callback();
			}.bind(this)
		});
	},
	componentDidMount: function(){
		this.loadPostsFromServer();
	},
	render: function(){
		return(
			<div className='page'>
				<SearchBar onSearchSubmit={this.onSubmitSearchQuery} />
				<JobPostList data={this.state.data} />
			</div>
		);
	}
});

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ searchbar ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
var itemLists = ['states', 'cities', 'companies'];
var SearchBar = React.createClass({
	getInitialState: function() {
		var newJson = {keywords: '', jobtypes: []};
		return newJson;
	},
	clearSearchBar: function(){
		var newState = this.state;
		newState['keywords'] = '';
		itemLists.forEach((list) => {
			$('#'+ list).tokenInput("clear");
		});
		newState['jobtypes'] = this.state.jobtypes.map(item => {
			item.checked = true;
			return item;
		});
		this.replaceState(newState);
	},
	componentDidMount: function(){
		var jobtypes = [{'id': '0', 'name': 'Full-time'}, {'id': '1', 'name': 'Part-time'}, {'id': '2', 'name': 'Temp'}];
		var all_items_checked = jobtypes.map(function(item){
			item.checked = true;
			return item;
		});
		this.setState({'jobtypes' : all_items_checked});
	},
	handleKeywordsChange: function(event) {
    	this.setState({keywords: event.target.value});
    },
	handleSubmit: function(e){
		var request = {};
		if(this.state.keywords != "")
			request['keywords'] = this.state.keywords;
		var listRequestData = this.state['jobtypes'].filter(item => (item.checked)).map( item => item.id );
		if(listRequestData.length != 3)
			request['jobtypes'] = listRequestData;
		itemLists.forEach((list) => {
			var ids = $('#'+ list).tokenInput("get").map(item => item.id);
			if(ids.length != 0)
				request[list] = ids;
		});
		this.props.onSearchSubmit(request, this.clearSearchBar);
	},
	handleJobTypeOptionToggle: function(item_id){
		var newState = {};
		newState['jobtypes'] = this.state['jobtypes'].map(function(item){
			if(item.id == item_id)
				item.checked = ! item.checked;
			return item;
		});
		this.setState(newState);
	},
	render: function(){
		var itemListsNodes = itemLists.map(function(list,i){
			return (
				<InputAutocomplete  key={i}  name={list} />
			);
		}.bind(this));
		return (
			<div className='searchbar'>
				<SearchLine value={this.state.keywords} onChange={this.handleKeywordsChange}/>
				<JobTypeItemsList items={this.state['jobtypes']} onOptionToggle={this.handleJobTypeOptionToggle}
					onToggleAll={this.handleJobTypeToggleAll} />
				{itemListsNodes}
	  		<div className='menu-item menu-button' onClick={this.handleSubmit}>search</div>
			</div>
		);
	}
});

var InputAutocomplete = React.createClass({
  componentDidMount: function() {
    $("#"+this.props.name).tokenInput('/api/' + this.props.name,
			{
				searchDelay: 0,
				minChars: 1,
				tokenLimit: 5,
				hintText: "choose " +  this.props.name,
				noResultsText: "not found",
				searchingText: "..."
			}
	);
  },
	render: function(){
		return(
      <div className='autocomplete-container'>
          <input type="text" id={this.props.name} name={this.props.name} placeholder={'choose '+this.props.name}/>
      </div>
		);
	}
});

var SearchLine = React.createClass({
	render: function() {
		return (
			<div className='searchword-container'>
				<div className='searchword'>Search: </div>
				<input type="text" className='menu-search-line' value={this.props.value} onChange={this.props.onChange} placeholder="please enter keywords"/>
			</div>
		);
	}
});

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ JobTypeItemsList ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

var JobTypeItemsList = React.createClass({
	getInitialState: function(){
		return {data:[]};
	},
	render: function(){
		if(this.props.items == undefined){
			return(
				<div className='menu-container menu-dropdown'>
					<div className="menu-item item-name">{this.props.listName}</div>
					<div className="menu-options-container"></div>
				</div>
			);
		}
		var	items_nodes = this.props.items.map(function(item){
				return (
					<ItemOption key={item.id} id={item.id} name={item.name}
						onOptionToggle={this.props.onOptionToggle}
						checked={item.checked} />
				);
		}.bind(this));
		return(
			<div className='menu-container menu-dropdown'>
				<div className="menu-item item-name">Job Type</div>
				<div className="menu-options-container">
					{items_nodes}
  			</div>
			</div>
		);
	}
});

var ItemOption = React.createClass({
	render: function(){
		var checkboxClass = (this.props.checked) ? "checkbox checkedCheckbox" : "checkbox uncheckedCheckbox";
		return(
			<div className="menu-item menu-option" onClick={this.props.onOptionToggle.bind(null, this.props.id)} >
  				<div className="menu-option-name">{this.props.name}</div>
  				<div className="menuOptionCheckbox">
					<label className={checkboxClass}></label>
				</div>
			</div>
		);

	}
});

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ JobPostList ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

var JobPostList = React.createClass({
	getInitialState: function(){
		return ({searchCommited: false});
	},
	componentDidMount: function(){
		this.state.searchCommited = true;
	},
	render: function(){
		if(this.props.data.length == 0)
		return(
			<div className = 'jobPostList'>
				<div className = 'altText'>
					<h1 className = 'not-found'>
					{this.state.searchCommited ? "Sorry, nothing was found :(" : "Loading"}
					</h1>
				</div>
			</div>
		);
		var jobPostNodes = this.props.data.map(function(jobPost, i){
			return(
				<JobPost key={i} data={jobPost}>
					{jobPost.postContent}
				</JobPost>
				);
		});

		return(
			<div className = 'jobPostList'>
				{jobPostNodes}
			</div>
		);
	}
});

var optional = [['state_name', 'State'], ['city_name', 'City'], [ 'company_name', 'Company'], [ 'email', 'Email' ]];

var JobPost = React.createClass({
	handlePostClick: function(event, link){
		if(link != undefined){
		  	var win=window.open(link, '_blank');
	  		win.focus();
  		}
	},
	getOptionalPostDetails: function(){
		var optionalNodes = optional.filter(field => (this.props.data[field[0]] != undefined && this.props.data[field[0]].length != 0))
			.map( (field, i) => {
				if (field[0] == 'email'){
					if( this.props.data['email'] == 'None')
						return ;
					return(
						<div key={i+5} className = 'jobDetails clickable blue' onClick={this.handlePostClick.bind(null, null, 'mailto:'+this.props.data.email)}>
							{field[1] + ': '}
							<u> {this.props.data['email']} </u>
						</div>
						);
				}
				return (
					<div className = 'jobDetails inline-info' key={i+5}>
						{field[1] + ': ' + this.props.data[field[0]]}
					</div>
					);
			});
		return optionalNodes;
	},
	render: function(){
		var optionalDetailsNode = this.getOptionalPostDetails();
		var employment_form;
		if(this.props.data.employment_form == "0")
			employment_form = "Full time";
		else if(this.props.data.employment_form == "1")
			employment_form = "Part time";
		else
			employment_form = "Temp";
		var working_manner_div = (this.props.data.working_manner == "0") ? "" :
			(<div className = 'jobDetails' key={4}>Working from home
			</div>);
		var story_id = this.props.data.post_story_id
		story_id = (story_id.indexOf('_') == -1)
			? story_id
			: story_id.substring(story_id.indexOf('_')+1, story_id.length);
		return(
			<div className = 'jobPost clickable' 	onClick={this.handlePostClick.bind(null, null,
									'https://www.facebook.com/groups/'+this.props.data.group_fb_id+'/permalink/'+story_id)}>
				<div className = 'groupTitle'>
					<div className = 'jobDetails clickable groupName' key='1' onClick={
						this.handlePostClick.bind(null, null,
							"https://www.facebook.com/groups/" + this.props.data.group_fb_id)}>
						<u>{this.props.data.group_name}</u>
					</div>
					<div className = 'jobDetails' key='2'>
						Published at: {this.props.data.publish_date}
					</div>
					<div className = 'jobDetails' key='3'>
						Work type: {employment_form}
					</div>
					{working_manner_div}
					{optionalDetailsNode}
				</div>
				<div className = 'postContent'>
					{this.props.data.full_post_body}
				</div>
			</div>
		);
	}
});


ReactDOM.render(
	<Page url='/api/jobposts' /> ,
	document.getElementById('content')
);
