import chromadb
from chromadb.config import Settings
import json
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CommercialChromaDBManager:
    def __init__(self, path: str = "./chroma_db"):
        self.client = None
        self.contracts_collection = None
        self.analysis_collection = None
        self.regulations_collection = None
        self.path = path
        self.initialized = False
    
    def initialize_db(self):
        """Initialize ChromaDB client and collection with commercial settings"""
        try:
            self.client = chromadb.PersistentClient(
                path=self.path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Create or get collections
            self.contracts_collection = self.client.get_or_create_collection(
                name="commercial_contracts",
                metadata={
                    "description": "Commercial contract compliance analysis storage",
                    "created": datetime.now().isoformat(),
                    "version": "2.0.0"
                }
            )
            
            self.analysis_collection = self.client.get_or_create_collection(
                name="compliance_analyses",
                metadata={
                    "description": "Compliance analysis results and metadata",
                    "created": datetime.now().isoformat(),
                    "version": "2.0.0"
                }
            )
            
            self.regulations_collection = self.client.get_or_create_collection(
                name="regulatory_knowledge",
                metadata={
                    "description": "Regulatory knowledge and compliance rules",
                    "created": datetime.now().isoformat(),
                    "version": "2.0.0"
                }
            )
            
            self.initialized = True
            logger.info("✅ Commercial ChromaDB initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing ChromaDB: {e}")
            self.initialized = False
            return False
    
    def is_connected(self) -> bool:
        """Check if ChromaDB is connected and initialized"""
        return self.initialized and self.contracts_collection is not None
    
    def store_contract(self, contract_text: str, metadata: Dict[str, Any]) -> bool:
        """Store contract analysis in ChromaDB with enhanced metadata"""
        if not self.is_connected():
            return False
        
        try:
            # Generate unique IDs
            contract_id = str(uuid.uuid4())
            analysis_id = metadata.get('analysis_id', str(uuid.uuid4()))
            
            # Convert lists to strings for ChromaDB compatibility
            processed_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, list):
                    processed_metadata[key] = json.dumps(value)  # Convert list to JSON string
                else:
                    processed_metadata[key] = value
            
            # Prepare contract metadata
            contract_metadata = {
                **processed_metadata,
                "contract_id": contract_id,
                "analysis_id": analysis_id,
                "storage_timestamp": datetime.now().isoformat(),
                "text_length": len(contract_text),
                "document_type": "contract"
            }
            
            # Prepare analysis metadata
            analysis_metadata = {
                **processed_metadata,
                "contract_id": contract_id,
                "analysis_id": analysis_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "document_type": "analysis"
            }
            
            # Ensure all metadata values are ChromaDB compatible
            contract_metadata = self._ensure_metadata_compatibility(contract_metadata)
            analysis_metadata = self._ensure_metadata_compatibility(analysis_metadata)
            
            # Store contract content
            self.contracts_collection.add(
                documents=[contract_text[:2000]],  # Store first 2000 chars for search
                metadatas=[contract_metadata],
                ids=[contract_id]
            )
            
            # Store analysis metadata
            self.analysis_collection.add(
                documents=[f"Analysis for contract {contract_id}"],
                metadatas=[analysis_metadata],
                ids=[analysis_id]
            )
            
            logger.info(f"✅ Contract stored successfully: {contract_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error storing contract: {e}")
            return False
    
    def _ensure_metadata_compatibility(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all metadata values are compatible with ChromaDB"""
        compatible_metadata = {}
        
        for key, value in metadata.items():
            if value is None:
                compatible_metadata[key] = ""
            elif isinstance(value, (str, int, float, bool)):
                compatible_metadata[key] = value
            elif isinstance(value, list):
                # Convert list to JSON string
                compatible_metadata[key] = json.dumps(value)
            elif isinstance(value, dict):
                # Convert dict to JSON string
                compatible_metadata[key] = json.dumps(value)
            else:
                # Convert any other type to string
                compatible_metadata[key] = str(value)
        
        return compatible_metadata
    
    def store_regulation_knowledge(self, regulation_data: Dict[str, Any]) -> bool:
        """Store regulatory knowledge for enhanced search"""
        if not self.is_connected():
            return False
        
        try:
            regulation_id = str(uuid.uuid4())
            
            # Ensure metadata compatibility
            compatible_metadata = self._ensure_metadata_compatibility({
                **regulation_data,
                "regulation_id": regulation_id,
                "storage_timestamp": datetime.now().isoformat(),
                "document_type": "regulation"
            })
            
            self.regulations_collection.add(
                documents=[regulation_data.get('description', '')],
                metadatas=[compatible_metadata],
                ids=[regulation_id]
            )
            
            return True
        except Exception as e:
            logger.error(f"❌ Error storing regulation: {e}")
            return False
    
    def search_contracts(self, query: str, n_results: int = 10) -> List[Dict]:
        """Enhanced contract search with multiple relevance strategies"""
        if not self.is_connected():
            return []
        
        try:
            # Search in contracts collection
            contract_results = self.contracts_collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["metadatas", "documents", "distances"]
            )
            
            # Search in analyses collection for additional context
            analysis_results = self.analysis_collection.query(
                query_texts=[query],
                n_results=n_results//2,
                include=["metadatas", "documents", "distances"]
            )
            
            formatted_results = []
            
            # Process contract results
            if contract_results['documents']:
                for i, doc in enumerate(contract_results['documents'][0]):
                    metadata = contract_results['metadatas'][0][i]
                    # Parse JSON strings back to lists/dicts
                    parsed_metadata = self._parse_metadata(metadata)
                    
                    formatted_results.append({
                        "type": "contract",
                        "document": doc,
                        "metadata": parsed_metadata,
                        "relevance_score": 1 - (contract_results['distances'][0][i] if contract_results['distances'] else 0),
                        "match_type": "content"
                    })
            
            # Process analysis results
            if analysis_results['documents']:
                for i, doc in enumerate(analysis_results['documents'][0]):
                    metadata = analysis_results['metadatas'][0][i]
                    # Parse JSON strings back to lists/dicts
                    parsed_metadata = self._parse_metadata(metadata)
                    
                    formatted_results.append({
                        "type": "analysis",
                        "document": doc,
                        "metadata": parsed_metadata,
                        "relevance_score": 1 - (analysis_results['distances'][0][i] if analysis_results['distances'] else 0),
                        "match_type": "metadata"
                    })
            
            # Sort by relevance score and remove duplicates
            formatted_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Remove duplicates based on contract_id
            seen_contracts = set()
            unique_results = []
            for result in formatted_results:
                contract_id = result['metadata'].get('contract_id')
                if contract_id not in seen_contracts:
                    seen_contracts.add(contract_id)
                    unique_results.append(result)
            
            return unique_results[:n_results]
            
        except Exception as e:
            logger.error(f"❌ Error searching contracts: {e}")
            return []
    
    def _parse_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Parse JSON strings in metadata back to Python objects"""
        parsed_metadata = {}
        
        for key, value in metadata.items():
            if isinstance(value, str):
                # Try to parse JSON strings
                try:
                    parsed_value = json.loads(value)
                    parsed_metadata[key] = parsed_value
                except (json.JSONDecodeError, TypeError):
                    parsed_metadata[key] = value
            else:
                parsed_metadata[key] = value
        
        return parsed_metadata
    
    def get_analysis_history(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        """Get recent compliance analysis history"""
        if not self.is_connected():
            return []
        
        try:
            # Get all analyses and sort by timestamp
            all_results = self.analysis_collection.get(
                include=["metadatas"],
                limit=limit + offset
            )
            
            if not all_results['metadatas']:
                return []
            
            # Parse metadata for each result
            parsed_results = []
            for metadata in all_results['metadatas']:
                parsed_metadata = self._parse_metadata(metadata)
                parsed_results.append(parsed_metadata)
            
            # Sort by timestamp (newest first)
            sorted_metadatas = sorted(
                parsed_results,
                key=lambda x: x.get('analysis_timestamp', ''),
                reverse=True
            )
            
            # Apply offset and limit
            paginated_results = sorted_metadatas[offset:offset + limit]
            
            return paginated_results
            
        except Exception as e:
            logger.error(f"❌ Error getting analysis history: {e}")
            return []
    
    def get_contract_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about stored contracts and analyses"""
        if not self.is_connected():
            return {"error": "Database not connected"}
        
        try:
            contract_count = self.contracts_collection.count()
            analysis_count = self.analysis_collection.count()
            regulation_count = self.regulations_collection.count()
            
            # Get recent analyses for timeline
            recent_analyses = self.get_analysis_history(limit=100)
            
            # Calculate statistics
            jurisdictions = {}
            industries = {}
            regulations_used = {}
            
            for analysis in recent_analyses:
                jurisdiction = analysis.get('jurisdiction', 'unknown')
                industry = analysis.get('industry', 'unknown')
                regulations = analysis.get('regulations', [])
                
                jurisdictions[jurisdiction] = jurisdictions.get(jurisdiction, 0) + 1
                industries[industry] = industries.get(industry, 0) + 1
                
                if isinstance(regulations, list):
                    for regulation in regulations:
                        regulations_used[regulation] = regulations_used.get(regulation, 0) + 1
                elif isinstance(regulations, str):
                    # Handle case where regulations is stored as JSON string
                    try:
                        reg_list = json.loads(regulations)
                        for regulation in reg_list:
                            regulations_used[regulation] = regulations_used.get(regulation, 0) + 1
                    except:
                        pass
            
            return {
                "total_contracts": contract_count,
                "total_analyses": analysis_count,
                "total_regulations": regulation_count,
                "jurisdiction_distribution": jurisdictions,
                "industry_distribution": industries,
                "top_regulations": dict(sorted(regulations_used.items(), key=lambda x: x[1], reverse=True)[:10]),
                "database_size_mb": self._get_database_size(),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting stats: {e}")
            return {"error": str(e)}
    
    def _get_database_size(self) -> float:
        """Estimate database size in MB"""
        try:
            import os
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            return round(total_size / (1024 * 1024), 2)
        except:
            return 0.0
    
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            import os
            
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            
            shutil.copytree(self.path, backup_path)
            logger.info(f"✅ Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Backup failed: {e}")
            return False
    
    def cleanup_old_analyses(self, days_old: int = 30) -> int:
        """Clean up analyses older than specified days"""
        if not self.is_connected():
            return 0
        
        try:
            cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            deleted_count = 0
            
            # Get all analyses
            all_analyses = self.analysis_collection.get(include=["metadatas", "ids"])
            
            for i, metadata in enumerate(all_analyses['metadatas']):
                analysis_timestamp = metadata.get('analysis_timestamp')
                if analysis_timestamp:
                    try:
                        # Handle different timestamp formats
                        if 'T' in analysis_timestamp:
                            analysis_date = datetime.fromisoformat(analysis_timestamp.replace('Z', '+00:00'))
                        else:
                            analysis_date = datetime.strptime(analysis_timestamp, '%Y-%m-%d %H:%M:%S')
                        
                        if analysis_date.timestamp() < cutoff_date:
                            analysis_id = all_analyses['ids'][i]
                            # Also delete corresponding contract
                            contract_id = metadata.get('contract_id')
                            
                            self.analysis_collection.delete(ids=[analysis_id])
                            if contract_id:
                                self.contracts_collection.delete(ids=[contract_id])
                            
                            deleted_count += 1
                    except Exception as e:
                        logger.warning(f"Could not parse timestamp {analysis_timestamp}: {e}")
                        continue
            
            logger.info(f"✅ Cleaned up {deleted_count} old analyses")
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")
            return 0
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about all collections"""
        if not self.is_connected():
            return {}
        
        try:
            collections_info = {}
            
            # Contracts collection info
            contracts_count = self.contracts_collection.count()
            contracts_metadata = self.contracts_collection.metadata or {}
            collections_info['contracts'] = {
                'count': contracts_count,
                'metadata': contracts_metadata
            }
            
            # Analysis collection info
            analysis_count = self.analysis_collection.count()
            analysis_metadata = self.analysis_collection.metadata or {}
            collections_info['analysis'] = {
                'count': analysis_count,
                'metadata': analysis_metadata
            }
            
            # Regulations collection info
            regulations_count = self.regulations_collection.count()
            regulations_metadata = self.regulations_collection.metadata or {}
            collections_info['regulations'] = {
                'count': regulations_count,
                'metadata': regulations_metadata
            }
            
            return collections_info
            
        except Exception as e:
            logger.error(f"❌ Error getting collection info: {e}")
            return {}
    
    def reset_database(self) -> bool:
        """Reset the entire database (use with caution)"""
        try:
            if self.client:
                self.client.reset()
                self.initialized = False
                logger.warning("🗑️ Database reset completed")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Database reset failed: {e}")
            return False