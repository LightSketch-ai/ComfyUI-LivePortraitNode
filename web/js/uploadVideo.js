import { app } from "../../../scripts/app.js";
import { api } from '../../../scripts/api.js'

function fitHeight(node) {
    node.setSize([node.size[0], node.computeSize([node.size[0], node.size[1]])[1]])
    node?.graph?.setDirtyCanvas(true);
}

function chainCallback(object, property, callback) {
    if (object == undefined) {
        //This should not happen.
        console.error("Tried to add callback to non-existant object")
        return;
    }
    if (property in object) {
        const callback_orig = object[property]
        object[property] = function () {
            const r = callback_orig.apply(this, arguments);
            callback.apply(this, arguments);
            return r
        };
    } else {
        object[property] = callback;
    }
}

function addPreviewOptions(nodeType) {
    chainCallback(nodeType.prototype, "getExtraMenuOptions", function(_, options) {
        // The intended way of appending options is returning a list of extra options,
        // but this isn't used in widgetInputs.js and would require
        // less generalization of chainCallback
        let optNew = []
        try {
            const previewWidget = this.widgets.find((w) => w.name === "videopreview");

            let url = null
            if (previewWidget.videoEl?.hidden == false && previewWidget.videoEl.src) {
                //Use full quality video
                //url = api.apiURL('/view?' + new URLSearchParams(previewWidget.value.params));
                url = previewWidget.videoEl.src
            }
            if (url) {
                optNew.push(
                    {
                        content: "Open preview",
                        callback: () => {
                            window.open(url, "_blank")
                        },
                    },
                    {
                        content: "Save preview",
                        callback: () => {
                            const a = document.createElement("a");
                            a.href = url;
                            a.setAttribute("download", new URLSearchParams(previewWidget.value.params).get("filename"));
                            document.body.append(a);
                            a.click();
                            requestAnimationFrame(() => a.remove());
                        },
                    }
                );
            }
            if(options.length > 0 && options[0] != null && optNew.length > 0) {
                optNew.push(null);
            }
            options.unshift(...optNew);

        } catch (error) {
            console.log(error);
        }

    });
}

async function uploadFile(file) {
    try {
        // Wrap file in formdata so it includes filename
        const body = new FormData();
        const i = file.webkitRelativePath.lastIndexOf('/');
        const subfolder = file.webkitRelativePath.slice(0,i+1)
        const new_file = new File([file], file.name, {
            type: file.type,
            lastModified: file.lastModified,
        });
        body.append("image", new_file);
        if (i > 0) {
            body.append("subfolder", subfolder);
        }
        const resp = await api.fetchApi("/upload/image", {
            method: "POST",
            body,
        });

        if (resp.status === 200) {
            return resp.status
        } else {
            alert(resp.status + " - " + resp.statusText);
        }
    } catch (error) {
        alert(error);
    }
}
app.registerExtension({
	name: "LightSketch.VideoUploader",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData?.name == "LightSketch Live Portrait") {
            chainCallback(nodeType.prototype, "onNodeCreated", function() {
                const pathWidget = this.widgets.find((w) => w.name === 'video');
                console.log('pathWidget', pathWidget)
                const fileInput = document.createElement("input");
                chainCallback(this, "onRemoved", () => {
                    fileInput?.remove();
                });

                Object.assign(fileInput, {
                    type: "file",
                    accept: "video/webm,video/mp4,video/mkv,image/gif",
                    style: "display: none",
                    onchange: async () => {
                        if (fileInput.files.length) {
                            if (await uploadFile(fileInput.files[0]) != 200) {
                                //upload failed and file can not be added to options
                                return;
                            }
                            const filename = fileInput.files[0].name;
                            // console.log(nodeData.input.required.driving_video);
                            // nodeData.input.required.driving_video = filename;
                            console.log('Have set driving_video to', filename);
                            pathWidget.options.values.push(filename);
                            pathWidget.value = filename;
                            if (pathWidget.callback) {
                                pathWidget.callback(filename)
                            }
                        }
                    },
                });
                document.body.append(fileInput);
                let uploadWidget = this.addWidget("button", "choose video to upload", "image", () => {
                    //clear the active click event
                    app.canvas.node_widget = null
                    fileInput.click();
                });
                uploadWidget.options.serialize = false;
            });
		}
	}
});