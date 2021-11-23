$(function() {
	function ProbeViewModel(parameters) {
		var self = this;
		self.settings = undefined;
		self.btnProbe = undefined;
		self.checkStatus  = undefined;
		self.btnProbeIcon = undefined;
		self.btnProbeText = undefined;

                self.checkStatus  = function() {
                        $.ajax({
                                url: API_BASEURL + "plugin/server_probing",
                                type: "GET",
                                dataType: "json",
                                data: JSON.stringify({
                                        action: "None"
                                }),
                                contentType: "application/json; charset=UTF-8",
                                success:function(data) {
                                if ( data.on == "True") {
                                    document.getElementById("job_probe").style.color = "red";
                                } else {
                                    document.getElementById("job_probe").style.color = "green";
                                }
                                        },
                                error: function (data, status) {
                                        var options = {
                                                title: "Probeing failed.",
                                                text: data.responseText,
                                                hide: true,
                                                buttons: {
                                                        sticker: false,
                                                        closer: true
                                                },
                                                type: "error"
                                        };
                                        
                                }
                        });
                };

                self.btnProbeClick  = function() {
                        $.ajax({
                                url: API_BASEURL + "plugin/server_probing",
                                type: "GET",
                                dataType: "json",
                                data: JSON.stringify({
                                        action: "Toggle"
                                }),
                                contentType: "application/json; charset=UTF-8",
                                success:function(data) {
                                if ( data.on == "True") {
                                    document.getElementById("job_probe").style.color = "red";
                                } else {
                                    document.getElementById("job_probe").style.color = "green";
                                }
                                        },
                                error: function (data, status) {
                                        var options = {
                                                title: "Probeing failed.",
                                                text: data.responseText,
                                                hide: true,
                                                buttons: {
                                                        sticker: false,
                                                        closer: true
                                                },
                                                type: "error"
                                        };
                                        
                                }
                        });
                };

		self.initializeButton = function() {
			var buttonContainer = $('#job_print')[0].parentElement;
			buttonContainer.children[0].style.width = "100%";
			buttonContainer.children[0].style.marginBottom = "10px";
			buttonContainer.children[1].style.marginLeft = "0";
			
			self.btnProbe = document.createElement("button");
			self.btnProbe.id = "job_probe";
			self.btnProbe.classList.add("btn");
			self.btnProbe.classList.add("span4");
			self.btnProbe.addEventListener("click", self.btnProbeClick);
			
			self.btnProbeIcon = document.createElement("i");
			self.btnProbe.appendChild(self.btnProbeIcon);
			
			self.btnProbeText = document.createTextNode(" ");
			self.btnProbe.appendChild(self.btnProbeText);
			
			self.btnProbeText.nodeValue = " Probe";
                        self.btnProbeIcon.classList.add("fas", "fa-level-down-alt");

			buttonContainer.appendChild(self.btnProbe);
		};
		
		self.initializeButton();
                self.checkStatus();
	}
	
	OCTOPRINT_VIEWMODELS.push([
		ProbeViewModel
	]);
});
