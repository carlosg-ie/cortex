##########################################################################
#
#  Copyright (c) 2008-2013, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#     * Neither the name of Image Engine Design nor the names of any
#       other contributors to this software may be used to endorse or
#       promote products derived from this software without specific prior
#       written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import maya.cmds

import IECore
import IECoreScene
import IECoreMaya

class FromMayaParticleConverterTest( IECoreMaya.TestCase ) :

	def testSimple( self ) :

		particle = maya.cmds.particle( n = 'particles' )[0]
		particle = maya.cmds.listRelatives( particle, shapes = True )[0]

		converter = IECoreMaya.FromMayaShapeConverter.create( str( particle ), IECoreScene.PointsPrimitive.staticTypeId() )

		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreMaya.TypeId.FromMayaParticleConverter ) ) )

		particle = converter.convert()

		self.assert_( particle.isInstanceOf( IECoreScene.PointsPrimitive.staticTypeId() ) )
		self.assert_( particle.arePrimitiveVariablesValid() )
		self.assertEqual( particle.numPoints, maya.cmds.particle( 'particles', q = True, count = True ) )

		self.assert_( "P" in particle )
		self.assert_( particle["P"].data.isInstanceOf( IECore.TypeId.V3fVectorData ) )
		self.assertEqual( particle["P"].data.getInterpretation(), IECore.GeometricData.Interpretation.Point )
		self.assert_( "velocity" in particle )
		self.assert_( particle["velocity"].data.isInstanceOf( IECore.TypeId.V3fVectorData ) )
		self.assertEqual( particle["velocity"].data.getInterpretation(), IECore.GeometricData.Interpretation.Vector )

		# We don't get this by default, and we didn't request it
		self.failIf( "mass" in particle )

	def testEmitter( self ) :

		maya.cmds.emitter( speed = 2.00, rate = 1000, n = 'emitter' )
		particle = maya.cmds.particle( n = 'particles' )[0]
		particle = maya.cmds.listRelatives( particle, shapes = True )[0]
		maya.cmds.connectDynamic( 'particles', em = 'emitter' )

		maya.cmds.addAttr( particle, ln="ieParticleAttributes", dt="string")
		# ensure we can split on any of the following: ' ', ':', ','
		maya.cmds.setAttr( particle + ".ieParticleAttributes", "radiusPP,userScalar1PP:userScalar2PP userScalar3PP", type="string" )

		maya.cmds.addAttr( particle, ln="radiusPP", dt="doubleArray")
		maya.cmds.addAttr( particle, ln="radiusPP0", dt="doubleArray")

		maya.cmds.addAttr( particle, ln="userScalar1PP", dt="doubleArray")
		maya.cmds.addAttr( particle, ln="userScalar1PP0", dt="doubleArray")

		maya.cmds.addAttr( particle, ln="userScalar2PP", dt="doubleArray")
		maya.cmds.addAttr( particle, ln="userScalar2PP0", dt="doubleArray")

		maya.cmds.addAttr( particle, ln="userScalar3PP", dt="doubleArray")
		maya.cmds.addAttr( particle, ln="userScalar3PP0", dt="doubleArray")

		maya.cmds.addAttr( particle, ln="userScalar4PP", dt="doubleArray")
		maya.cmds.addAttr( particle, ln="userScalar4PP0", dt="doubleArray")

		for i in range( 0, 25 ) :
			maya.cmds.currentTime( i )

		converter = IECoreMaya.FromMayaShapeConverter.create( str( particle ), IECoreScene.PointsPrimitive.staticTypeId() )

		converter["attributeNames"] = IECore.StringVectorData( [ "velocity", "mass" ] )

		self.assert_( converter.isInstanceOf( IECore.TypeId( IECoreMaya.TypeId.FromMayaParticleConverter ) ) )

		particle = converter.convert()

		self.assert_( particle.isInstanceOf( IECoreScene.PointsPrimitive.staticTypeId() ) )
		self.assert_( particle.arePrimitiveVariablesValid() )
		self.assertEqual( particle.numPoints, maya.cmds.particle( 'particles', q = True, count = True ) )
		self.assert_( particle.numPoints > 900 )
		self.assert_( particle.numPoints < 1100 )
		self.assert_( "P" in particle )
		self.assert_( particle["P"].data.isInstanceOf( IECore.TypeId.V3fVectorData ) )
		self.assertEqual( particle["P"].data.getInterpretation(), IECore.GeometricData.Interpretation.Point )
		self.assert_( "velocity" in particle )
		self.assert_( particle["velocity"].data.isInstanceOf( IECore.TypeId.V3fVectorData ) )
		self.assertEqual( particle["velocity"].data.getInterpretation(), IECore.GeometricData.Interpretation.Vector )
		self.assert_( "mass" in particle )
		self.assert_( particle["mass"].data.isInstanceOf( IECore.TypeId.FloatVectorData ) )
		self.assert_( "radiusPP" in particle )
		self.assert_( particle["radiusPP"].data.isInstanceOf( IECore.TypeId.FloatVectorData ) )
		self.assert_( "userScalar1PP" in particle )
		self.assert_( particle["userScalar1PP"].data.isInstanceOf( IECore.TypeId.FloatVectorData ) )
		self.assert_( "userScalar2PP" in particle )
		self.assert_( particle["userScalar2PP"].data.isInstanceOf( IECore.TypeId.FloatVectorData ) )
		self.assert_( "userScalar3PP" in particle )
		self.assert_( particle["userScalar3PP"].data.isInstanceOf( IECore.TypeId.FloatVectorData ) )

		#userScalar4PP is defined on the particles not specified in ieParticleAttributes and therefore shouldn't be converted
		self.assert_( "userScalar4PP" not in particle )


	def testErrors( self ) :

		particle = maya.cmds.particle( n = 'particles' )[0]
		particle = maya.cmds.listRelatives( particle, shapes = True )[0]

		self.failIf( IECoreMaya.FromMayaShapeConverter.create( str( particle ), IECoreScene.MeshPrimitive.staticTypeId() ) )

if __name__ == "__main__":
	IECoreMaya.TestProgram()
