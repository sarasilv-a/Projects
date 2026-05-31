#ifndef PARSE_HPP
#define PARSE_HPP

#include "configuration.hpp"
#include "../include/fileUtils.hpp"
#include "../include/Point.hpp"
#include "../include/Point2D.hpp"
#include "../../libs/rapidxml/rapidxml.hpp"
#include "../../libs/rapidxml/rapidxml_utils.hpp"
#include <string>
#include <memory>

Configuration parseConfig(std::string filename);
Group parseGroup(rapidxml::xml_node<>* groupNode);
void parseTransform(rapidxml::xml_node<>* transformNode, Group& group);

#endif // PARSE_HPP
