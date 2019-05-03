//
//  ViewController.swift
//  timber_assemblies
//
//  Created by Yuta Akizuki on 3/7/19.
//  Copyright © 2019 ytakzk. All rights reserved.
//

import UIKit
import ARKit
import SceneKit
import SceneKit.ModelIO

class ViewController: UIViewController {

    override var prefersStatusBarHidden: Bool { return true }
    override var preferredStatusBarUpdateAnimation: UIStatusBarAnimation { return .slide }
    
    @IBOutlet weak var sceneView: ARSCNView!
    
    var modelNode: SCNNode?
    var planeNode: PlaneNode?
    var currentAngleY: Float = 0.0
    var startX: Float = 0.0

    let session = ARSession()

    override func viewDidLoad() {
        super.viewDidLoad()

        sceneView.session = session
        sceneView.showsStatistics = true
        sceneView.debugOptions = ARSCNDebugOptions.showFeaturePoints

    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        
        let configuration = ARWorldTrackingConfiguration()
        configuration.planeDetection = .horizontal
        configuration.isLightEstimationEnabled = true
        sceneView.session.run(configuration)
        
        
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        viewDidAppear(animated)
        
        sceneView.session.pause()
    }

    @IBAction func panned(_ sender: UIPanGestureRecognizer) {
        
        guard let modelNode = self.modelNode else { return }
        
        sender.minimumNumberOfTouches = 1
        
        let results = self.sceneView.hitTest(sender.location(in: sender.view), types: .existingPlaneUsingExtent)
        
        guard let result = results.first else { return }
        
        let position = SCNVector3Make(result.worldTransform.columns.3.x, result.worldTransform.columns.3.y, modelNode.position.z)
        
        modelNode.position = position
    }
    
    @IBAction func rotated(_ sender: UIRotationGestureRecognizer) {
    
        guard let modelNode = self.modelNode else { return }
        
        let rotation = Float(sender.rotation)
        
        if sender.state == .changed {
            
            modelNode.eulerAngles.y = currentAngleY + rotation
        }
        
        if sender.state == .ended {
            
            currentAngleY = modelNode.eulerAngles.y
        
        }

    }
    
    @IBAction func tapped(_ sender: UITapGestureRecognizer) {
    
        let touchPosition = sender.location(in: sceneView)

        let hitTestResult = sceneView.hitTest(touchPosition, types: .existingPlaneUsingExtent)
        
        guard !hitTestResult.isEmpty, let hitResult = hitTestResult.first else { return }
        
        DispatchQueue.main.async {
            
            if self.modelNode == nil {
                
                let moduleScene = SCNScene(named: "arts.scnassets/module.scn")
                self.modelNode = moduleScene?.rootNode.childNode(withName: "module", recursively: true)
                
                let beams  = self.modelNode?.childNode(withName: "beams", recursively: true)
                let dowels = self.modelNode?.childNode(withName: "dowels", recursively: true)
                
                if let children = beams?.childNodes {
                    
                    for c in children {
                        
                        if let geometry = c.geometry, let m = geometry.firstMaterial {
                            
                            m.diffuse.contents = UIColor.blue.withAlphaComponent(0.7)
                        }
                    }
                }
                
                if let children = dowels?.childNodes {
                    
                    for c in children {
                        
                        if let geometry = c.geometry, let m = geometry.firstMaterial {
                            
                            m.diffuse.contents = UIColor.green.withAlphaComponent(0.7)
                        }
                    }
                }
                
                self.modelNode?.scale = SCNVector3(0.001, 0.001, 0.001)
            
                self.sceneView.scene.rootNode.addChildNode(self.modelNode!)

            }

            self.modelNode?.position = SCNVector3(
                hitResult.worldTransform.columns.3.x,
                hitResult.worldTransform.columns.3.y,
                hitResult.worldTransform.columns.3.z)

        }
        
    }
    

}

extension ViewController: ARSCNViewDelegate {
    
    func renderer(_ renderer: SCNSceneRenderer, didAdd node: SCNNode, for anchor: ARAnchor) {
        
        DispatchQueue.main.async {

            if let planeAnchor = anchor as? ARPlaneAnchor {

                node.addChildNode(PlaneNode(anchor: planeAnchor) )
            }
        }
    }
    
    func renderer(_ renderer: SCNSceneRenderer, didUpdate node: SCNNode, for anchor: ARAnchor) {
        
        DispatchQueue.main.async {
            
            if let planeAnchor = anchor as? ARPlaneAnchor,
                let planeNode = node.childNodes[0] as? PlaneNode {

                planeNode.update(anchor: planeAnchor)
            }
        }
    }

}

